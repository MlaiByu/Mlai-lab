import os
import subprocess
import threading
import time
import datetime
import uuid
import random
import re
from flask import Blueprint, request, jsonify
from config import Config

container_bp = Blueprint('container', __name__)

running_containers = []
used_ports = set()
lock = threading.Lock()
user_container_count = {}

def get_user_container_count(user_id):
    return user_container_count.get(user_id, 0)

def increment_user_container_count(user_id):
    user_container_count[user_id] = user_container_count.get(user_id, 0) + 1

def decrement_user_container_count(user_id):
    user_container_count[user_id] = max(0, user_container_count.get(user_id, 0) - 1)

def _find_vulnerability_config(vulnerability_id):
    for name, tag in Config.DOCKER_VULN_MAP.items():
        if str(vulnerability_id) == str(tag) or str(vulnerability_id) == str(name):
            return name, tag
    
    try:
        from utils.db import get_vulnerability_by_id
        vuln = get_vulnerability_by_id(vulnerability_id)
        if vuln:
            vuln_name = vuln.get('name', '')
            for name, tag in Config.DOCKER_VULN_MAP.items():
                if vuln_name == name:
                    return name, tag
    except Exception as e:
        print(f"[ERROR] 查询数据库漏洞失败: {e}")
    
    return None, None

def run_docker_command(cmd, timeout=30, env=None):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )
        success = result.returncode == 0
        return success, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, '', '命令执行超时'
    except Exception as e:
        return False, '', str(e)

def docker_compose_up(docker_dir, project_name, host_port):
    env = os.environ.copy()
    env['COMPOSE_PROJECT_NAME'] = project_name
    env['HOST_PORT'] = str(host_port)
    
    success, stdout, stderr = run_docker_command(
        f"cd {docker_dir} && docker compose -p {project_name} up -d",
        timeout=180,
        env=env
    )
    if not success and 'docker compose' in stderr:
        success, stdout, stderr = run_docker_command(
            f"cd {docker_dir} && docker-compose -p {project_name} up -d",
            timeout=180,
            env=env
        )
    return success, stdout, stderr

def docker_compose_down(docker_dir, project_name, remove_volumes=False):
    cmd = f"cd {docker_dir} && docker compose -p {project_name} down"
    if remove_volumes:
        cmd += " -v"
    
    print(f"[DEBUG] 执行命令: {cmd}")
    success, stdout, stderr = run_docker_command(cmd, timeout=60)
    print(f"[DEBUG] 命令结果: success={success}, stdout={stdout[:100]}, stderr={stderr[:100]}")
    
    if not success and 'docker compose' in stderr:
        cmd = f"cd {docker_dir} && docker-compose -p {project_name} down"
        if remove_volumes:
            cmd += " -v"
        print(f"[DEBUG] 重试命令: {cmd}")
        success, stdout, stderr = run_docker_command(cmd, timeout=60)
        print(f"[DEBUG] 重试结果: success={success}, stdout={stdout[:100]}, stderr={stderr[:100]}")
    
    return success, stdout, stderr

def get_container_id_from_compose(docker_dir, project_name):
    for _ in range(10):
        success, stdout, _ = run_docker_command(
            f'cd {docker_dir} && docker compose -p {project_name} ps -q web',
            timeout=5
        )
        if success and stdout.strip():
            return stdout.strip()[:12]
        time.sleep(0.3)
    return None

def is_container_running(container_id):
    try:
        success, stdout, _ = run_docker_command(
            f"docker inspect --format='{{{{.State.Running}}}}' {container_id}",
            timeout=5
        )
        return success and stdout.strip() == 'true'
    except:
        return False

def cleanup_docker_resources(project_name):
    try:
        run_docker_command(f"docker rm -f $(docker ps -q --filter name={project_name})", timeout=10)
    except:
        pass
    try:
        run_docker_command(f"docker network rm $(docker network ls -q --filter name={project_name})", timeout=10)
    except:
        pass
    try:
        run_docker_command(f"docker volume rm $(docker volume ls -q --filter name={project_name})", timeout=10)
    except:
        pass

def cleanup_expired_containers():
    current_time = time.time()
    expired = []
    with lock:
        for c in running_containers:
            if c.get('timeout_at') and current_time > c['timeout_at']:
                expired.append(c.copy())
    for c in expired:
        _async_remove(c)

def schedule_cleanup():
    while True:
        cleanup_expired_containers()
        time.sleep(60)

cleanup_thread = threading.Thread(target=schedule_cleanup, daemon=True)
cleanup_thread.start()

def _do_remove(container_info, sync=False):
    cid = container_info.get('id')
    pn = container_info.get('project_name')
    dd = container_info.get('docker_dir')
    hp = container_info.get('host_port')
    uid = container_info.get('user_id')
    sid = container_info.get('session_db_id')
    use_compose = container_info.get('use_docker_compose', False)
    
    print(f"[CONTAINER] 开始删除容器: id={cid}, name={pn}, use_compose={use_compose}, docker_dir={dd}, sync={sync}")
    
    success = False
    
    try:
        if use_compose and pn and dd:
            print(f"[CONTAINER] 使用docker-compose down: {pn}")
            success, stdout, stderr = docker_compose_down(dd, pn, remove_volumes=True)
            if success:
                print(f"[CONTAINER] docker-compose down成功: {pn}")
            else:
                print(f"[CONTAINER] docker-compose down失败: {stderr}")
                cleanup_docker_resources(pn)
        elif cid:
            print(f"[CONTAINER] 检查容器状态: {cid}")
            if is_container_running(cid):
                print(f"[CONTAINER] 强制删除容器: {cid}")
                success, stdout, stderr = run_docker_command(f"docker rm -f {cid}", timeout=15)
                if success:
                    print(f"[CONTAINER] 容器删除成功: {cid}")
            else:
                print(f"[CONTAINER] 容器已停止或不存在: {cid}")
                success, stdout, stderr = run_docker_command(f"docker rm {cid} 2>/dev/null || true", timeout=10)
                success = True
        
        if pn:
            cleanup_docker_resources(pn)
    
    except Exception as e:
        print(f"[ERROR] 容器删除失败: {e}")
        try:
            if pn:
                cleanup_docker_resources(pn)
            if cid:
                run_docker_command(f"docker rm -f {cid} 2>/dev/null || true", timeout=10)
        except Exception as cleanup_e:
            print(f"[ERROR] 强制清理失败: {cleanup_e}")
        success = False
    
    with lock:
        if cid:
            running_containers[:] = [c for c in running_containers if c.get('id') != cid]
        if pn:
            running_containers[:] = [c for c in running_containers if c.get('project_name') != pn]
        if hp:
            used_ports.discard(hp)
        if uid:
            decrement_user_container_count(uid)
    
    print(f"[CONTAINER] 容器删除完成: id={cid}, name={pn}, success={success}")
    
    if uid and sid:
        try:
            from utils.db import update_experiment_session
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            from utils.db import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT success FROM experiment_sessions WHERE id = %s', (sid,))
            result = cursor.fetchone()
            conn.close()
            current_success = result['success'] if result else 0
            if current_success == 0:
                update_experiment_session(sid, end_time=now, success=0)
            else:
                update_experiment_session(sid, end_time=now)
        except Exception as e:
            print(f"[ERROR] 更新会话失败: {e}")
    
    return success

def _async_remove(container_info):
    def _remove():
        _do_remove(container_info, sync=False)
    
    threading.Thread(target=_remove, daemon=True).start()

pending_operations = {}

def _cleanup_user_containers(user_id):
    stopped_containers = []
    
    with lock:
        user_containers = [c.copy() for c in running_containers if c.get('user_id') == user_id]
    
    for c in user_containers:
        print(f"[INFO] 停止容器: {c.get('id')}")
        _async_remove(c)
        stopped_containers.append(c)
    
    try:
        from utils.db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, docker_container_id FROM experiment_sessions WHERE user_id = %s AND end_time IS NULL AND docker_container_id IS NOT NULL",
            (user_id,)
        )
        sessions = cursor.fetchall()
        conn.close()
        
        for s in sessions:
            cid = s.get('docker_container_id')
            if cid and cid not in [sc.get('id') for sc in stopped_containers]:
                print(f"[INFO] 从数据库中找到未结束的容器: {cid}，正在停止...")
                run_docker_command(f"docker rm -f {cid}", timeout=15)
                cleanup_docker_resources(cid)
    except Exception as e:
        print(f"[ERROR] 清理数据库中旧容器失败: {e}")

def _do_create_container(vulnerability_id, user_id, session_db_id, operation_id):
    try:
        vulnerability_name, type_tag = _find_vulnerability_config(vulnerability_id)
        
        if not vulnerability_name or not type_tag:
            with lock:
                pending_operations[operation_id] = {
                    'status': 'failed',
                    'error': '漏洞类型不存在',
                    'timestamp': time.time()
                }
            return
        
        _cleanup_user_containers(user_id)
        
        cleanup_expired_containers()
        
        project_name = f"mlaic_{type_tag[:8]}_{uuid.uuid4().hex[:6]}"
        docker_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docker', type_tag))
        
        if not os.path.exists(docker_dir):
            with lock:
                pending_operations[operation_id] = {
                    'status': 'failed',
                    'error': '漏洞环境不存在',
                    'timestamp': time.time()
                }
            return
        
        host_port = get_available_port()
        if not host_port:
            with lock:
                pending_operations[operation_id] = {
                    'status': 'failed',
                    'error': '没有可用端口',
                    'timestamp': time.time()
                }
            return
        
        config = Config.DOCKER_CONFIGS.get(vulnerability_name, {})
        use_compose = config.get('use_docker_compose', False)
        
        container_id = None
        
        if use_compose:
            success, stdout, stderr = docker_compose_up(docker_dir, project_name, host_port)
            if not success:
                with lock:
                    used_ports.discard(host_port)
                try:
                    docker_compose_down(docker_dir, project_name)
                    cleanup_docker_resources(project_name)
                except:
                    pass
                with lock:
                    pending_operations[operation_id] = {
                        'status': 'failed',
                        'error': f'启动失败: {stderr}',
                        'timestamp': time.time()
                    }
                return
            
            container_id = get_container_id_from_compose(docker_dir, project_name)
            if not container_id:
                with lock:
                    used_ports.discard(host_port)
                docker_compose_down(docker_dir, project_name)
                with lock:
                    pending_operations[operation_id] = {
                        'status': 'failed',
                        'error': '容器启动超时',
                        'timestamp': time.time()
                    }
                return
        else:
            image = config.get('image', 'php:7.4-apache')
            container_port = config.get('port', 80)
            volumes = config.get('volumes', {})
            env_vars = config.get('env', {})
            cmd_extra = config.get('command', '')
            
            volume_str = ' '.join(f"-v {os.path.join(docker_dir, hp)}:{cp}" for hp, cp in volumes.items())
            env_str = ' '.join(f"-e {k}={v}" for k, v in env_vars.items())
            full_cmd = f"docker run -d --name {project_name} -p {host_port}:{container_port} --memory=512m --cpus=0.7 {volume_str} {env_str} --label {Config.CONTAINER_LABEL}={vulnerability_name} --stop-timeout 10 {image} {cmd_extra}"
            
            success, stdout, stderr = run_docker_command(full_cmd, timeout=30)
            if not success:
                with lock:
                    used_ports.discard(host_port)
                with lock:
                    pending_operations[operation_id] = {
                        'status': 'failed',
                        'error': f'启动失败: {stderr}',
                        'timestamp': time.time()
                    }
                return
            container_id = stdout.strip()[:12]
        
        container_info = {
            'id': container_id,
            'name': project_name,
            'status': 'running',
            'vulnerability_id': vulnerability_id,
            'vulnerability_name': vulnerability_name,
            'host_port': host_port,
            'use_docker_compose': use_compose,
            'project_name': project_name,
            'docker_dir': docker_dir,
            'user_id': user_id,
            'session_db_id': session_db_id,
            'timeout_at': time.time() + Config.EXPERIMENT_TIMEOUT,
            'created_at': time.time()
        }
        
        with lock:
            running_containers.append(container_info)
            increment_user_container_count(user_id)
        
        try:
            from utils.db import update_experiment_session
            update_experiment_session(session_db_id, docker_container_id=container_info['id'], server_port=container_info['host_port'])
        except Exception as e:
            print(f"[ERROR] 更新会话容器信息失败: {e}")
        
        with lock:
            container_info['container_id'] = container_info['id']
            pending_operations[operation_id] = {
                'status': 'completed',
                'container_info': container_info,
                'timestamp': time.time()
            }
            
    except Exception as e:
        print(f"[ERROR] 异步创建容器失败: {e}")
        with lock:
            pending_operations[operation_id] = {
                'status': 'failed',
                'error': str(e),
                'timestamp': time.time()
            }

def _create_container_sync(vulnerability_id, user_id, session_db_id):
    vulnerability_name, type_tag = _find_vulnerability_config(vulnerability_id)
    
    if not vulnerability_name or not type_tag:
        return None, '漏洞类型不存在'
    
    _cleanup_user_containers(user_id)
    cleanup_expired_containers()
    
    project_name = f"mlaic_{type_tag[:8]}_{uuid.uuid4().hex[:6]}"
    docker_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docker', type_tag))
    
    if not os.path.exists(docker_dir):
        return None, '漏洞环境不存在'
    
    host_port = get_available_port()
    if not host_port:
        return None, '没有可用端口'
    
    config = Config.DOCKER_CONFIGS.get(vulnerability_name, {})
    use_compose = config.get('use_docker_compose', False)
    
    container_id = None
    
    if use_compose:
        success, stdout, stderr = docker_compose_up(docker_dir, project_name, host_port)
        if not success:
            with lock:
                used_ports.discard(host_port)
            try:
                docker_compose_down(docker_dir, project_name)
                cleanup_docker_resources(project_name)
            except:
                pass
            return None, f'启动失败: {stderr}'
        
        container_id = get_container_id_from_compose(docker_dir, project_name)
        if not container_id:
            with lock:
                used_ports.discard(host_port)
            docker_compose_down(docker_dir, project_name)
            return None, '容器启动超时'
    else:
        image = config.get('image', 'php:7.4-apache')
        container_port = config.get('port', 80)
        volumes = config.get('volumes', {})
        env_vars = config.get('env', {})
        cmd_extra = config.get('command', '')
        
        volume_str = ' '.join(f"-v {os.path.join(docker_dir, hp)}:{cp}" for hp, cp in volumes.items())
        env_str = ' '.join(f"-e {k}={v}" for k, v in env_vars.items())
        full_cmd = f"docker run -d --name {project_name} -p {host_port}:{container_port} --memory=512m --cpus=0.7 {volume_str} {env_str} --label {Config.CONTAINER_LABEL}={vulnerability_name} --stop-timeout 10 {image} {cmd_extra}"
        
        success, stdout, stderr = run_docker_command(full_cmd, timeout=30)
        if not success:
            with lock:
                used_ports.discard(host_port)
            return None, f'启动失败: {stderr}'
        container_id = stdout.strip()[:12]
    
    container_info = {
        'id': container_id,
        'name': project_name,
        'status': 'running',
        'vulnerability_id': vulnerability_id,
        'vulnerability_name': vulnerability_name,
        'host_port': host_port,
        'use_docker_compose': use_compose,
        'project_name': project_name,
        'docker_dir': docker_dir,
        'user_id': user_id,
        'session_db_id': session_db_id,
        'timeout_at': time.time() + Config.EXPERIMENT_TIMEOUT,
        'created_at': time.time()
    }
    
    with lock:
        running_containers.append(container_info)
        increment_user_container_count(user_id)
    
    try:
        from utils.db import update_experiment_session
        update_experiment_session(session_db_id, docker_container_id=container_info['id'], server_port=container_info['host_port'])
    except Exception as e:
        print(f"[ERROR] 更新会话容器信息失败: {e}")
    
    return container_info, None

@container_bp.route('/api/container/create', methods=['POST'])
def create_container():
    try:
        data = request.get_json() if request.is_json else {}
        vulnerability_id = data.get('vulnerability_id', data.get('vulnerabilityId', 0))
        user_id = data.get('user_id', data.get('userId', 0))
        session_db_id = data.get('session_db_id', data.get('sessionDbId', 0))
        async_mode = data.get('async', False)
        
        if not vulnerability_id:
            return jsonify({'success': False, 'message': '漏洞ID不能为空'}), 400
        
        if async_mode:
            operation_id = uuid.uuid4().hex
            with lock:
                pending_operations[operation_id] = {
                    'status': 'pending',
                    'timestamp': time.time()
                }
            
            threading.Thread(target=_do_create_container, args=(vulnerability_id, user_id, session_db_id, operation_id), daemon=True).start()
            
            return jsonify({
                'success': True,
                'operation_id': operation_id,
                'message': '容器创建请求已提交，请稍后查询状态'
            })
        else:
            container_info, error = _create_container_sync(vulnerability_id, user_id, session_db_id)
            
            if error:
                return jsonify({'success': False, 'message': error}), 500
            
            container_info['container_id'] = container_info.get('id')
            
            return jsonify(container_info)
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@container_bp.route('/api/container/create/status/<operation_id>', methods=['GET'])
def get_container_create_status(operation_id):
    try:
        with lock:
            status = pending_operations.get(operation_id)
        
        if not status:
            return jsonify({'success': False, 'message': '操作不存在'}), 404
        
        if status['status'] == 'completed':
            with lock:
                del pending_operations[operation_id]
            return jsonify({
                'success': True,
                'status': 'completed',
                'container_info': status['container_info']
            })
        elif status['status'] == 'failed':
            with lock:
                del pending_operations[operation_id]
            return jsonify({
                'success': False,
                'status': 'failed',
                'message': status['error']
            })
        else:
            return jsonify({
                'success': True,
                'status': 'pending',
                'message': '容器正在创建中...'
            })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@container_bp.route('/api/container/remove/<container_id>', methods=['POST'])
def remove_container(container_id):
    try:
        data = request.get_json() if request.is_json else {}
        user_id = data.get('user_id', data.get('userId', 0))
        session_db_id = data.get('session_db_id', data.get('sessionDbId', 0))
        sync = data.get('sync', data.get('Sync', True))
        
        container_info = None
        with lock:
            for c in running_containers:
                c_id = c.get('id', '')
                c_name = c.get('name', '')
                c_project_name = c.get('project_name', '')
                
                if (c_id == container_id or 
                    c_id.startswith(container_id) or 
                    c_name == container_id or 
                    c_project_name == container_id):
                    container_info = c.copy()
                    break
        
        if not container_info:
            success_id, stdout_id, _ = run_docker_command(f"docker ps -q --no-trunc --filter id={container_id}", timeout=5)
            success_name, stdout_name, _ = run_docker_command(f"docker ps -q --no-trunc --filter name={container_id}", timeout=5)
            
            if not stdout_id.strip() and not stdout_name.strip():
                print(f"[INFO] 容器不存在: {container_id}")
                return jsonify({'success': True, 'message': '容器已不存在'})
            
            full_id = stdout_id.strip() if stdout_id.strip() else stdout_name.strip()
            if len(full_id) > 12:
                short_id = full_id[:12]
            else:
                short_id = full_id
            
            container_info = {
                'id': short_id,
                'project_name': container_id,
                'user_id': user_id,
                'session_db_id': session_db_id
            }
        
        with lock:
            cid = container_info.get('id')
            pn = container_info.get('project_name')
            hp = container_info.get('host_port')
            uid = container_info.get('user_id')
            
            if cid:
                running_containers[:] = [c for c in running_containers if c.get('id') != cid]
            if pn:
                running_containers[:] = [c for c in running_containers if c.get('project_name') != pn]
            if hp:
                used_ports.discard(hp)
            if uid:
                decrement_user_container_count(uid)
        
        if sync:
            print(f"[INFO] 同步删除容器: {container_id}")
            remove_success = _do_remove(container_info, sync=True)
            return jsonify({
                'success': True, 
                'message': remove_success and '容器已成功删除' or '容器删除完成（可能已不存在）'
            })
        else:
            print(f"[INFO] 异步删除容器: {container_id}")
            _async_remove(container_info)
            
            if session_db_id:
                try:
                    from utils.db import update_experiment_session, get_db_connection
                    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('SELECT success FROM experiment_sessions WHERE id = %s', (session_db_id,))
                    result = cursor.fetchone()
                    conn.close()
                    current_success = result['success'] if result else 0
                    if current_success == 0:
                        update_experiment_session(session_db_id, end_time=now, success=0)
                    else:
                        update_experiment_session(session_db_id, end_time=now)
                except:
                    pass
            
            return jsonify({'success': True, 'message': '容器删除任务已提交'})
    
    except Exception as e:
        print(f"[ERROR] 删除容器异常: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@container_bp.route('/api/container/list', methods=['GET'])
def list_containers():
    try:
        user_id = request.args.get('user_id', request.args.get('userId', 0))
        
        # 从数据库获取活跃会话
        from utils.db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT id, session_id, user_id, vulnerability_id, docker_container_id, server_port, start_time 
                FROM experiment_sessions 
                WHERE end_time IS NULL AND user_id = %s
            ''', (int(user_id),))
        else:
            cursor.execute('''
                SELECT id, session_id, user_id, vulnerability_id, docker_container_id, server_port, start_time 
                FROM experiment_sessions 
                WHERE end_time IS NULL
            ''')
        
        sessions = cursor.fetchall()
        conn.close()
        
        # 从Docker获取实际运行的容器信息
        success, stdout, _ = run_docker_command(
            "docker ps --format '{{.ID}}|{{.Names}}|{{.Ports}}' 2>/dev/null",
            timeout=10
        )
        
        docker_containers = {}
        if success and stdout.strip():
            for line in stdout.strip().split('\n'):
                parts = line.split('|')
                if len(parts) >= 3:
                    cid = parts[0][:12]
                    name = parts[1]
                    ports = parts[2]
                    port_match = re.search(r':(\d+)->', ports)
                    host_port = int(port_match.group(1)) if port_match else None
                    docker_containers[cid] = {'name': name, 'host_port': host_port}
        
        # 将数据库会话与Docker容器匹配
        containers_with_id = []
        for session in sessions:
            docker_cid = session.get('docker_container_id')
            if not docker_cid:
                continue
            
            cid = docker_cid[:12]
            if cid in docker_containers:
                docker_info = docker_containers[cid]
                
                # 获取漏洞名称
                from utils.db import get_db_connection
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT name FROM vulnerabilities WHERE id = %s', (session['vulnerability_id'],))
                vuln = cursor.fetchone()
                vulnerability_name = vuln.get('name') if vuln else 'Unknown'
                conn.close()
                
                # 计算超时时间
                timeout_at = None
                start_time = session.get('start_time')
                if start_time:
                    import datetime
                    if isinstance(start_time, str):
                        start_dt = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                    else:
                        start_dt = start_time
                    timeout_dt = start_dt + datetime.timedelta(seconds=Config.EXPERIMENT_TIMEOUT)
                    timeout_at = timeout_dt.timestamp()
                
                container_info = {
                    'id': cid,
                    'container_id': cid,
                    'name': docker_info['name'],
                    'project_name': docker_info['name'],
                    'status': 'running',
                    'host_port': docker_info['host_port'] or session.get('server_port'),
                    'user_id': session['user_id'],
                    'vulnerability_id': session['vulnerability_id'],
                    'vulnerability_name': vulnerability_name,
                    'session_db_id': session['id'],
                    'session_id': session.get('session_id'),
                    'timeout_at': timeout_at
                }
                containers_with_id.append(container_info)
        
        return jsonify({'success': True, 'containers': containers_with_id})
    
    except Exception as e:
        print(f"[ERROR] list_containers: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@container_bp.route('/api/container/status/<container_id>', methods=['GET'])
def get_container_status(container_id):
    try:
        container_info = None
        with lock:
            for c in running_containers:
                if c['id'] == container_id or c.get('name') == container_id:
                    container_info = c
                    break
        
        if container_info:
            return jsonify({'success': True, 'status': container_info.get('status', 'running'), 'container': container_info})
        
        success, stdout, _ = run_docker_command(f"docker inspect --format='{{{{.State.Running}}}}' {container_id}", timeout=5)
        status = 'running' if success and stdout.strip() == 'true' else 'stopped'
        
        return jsonify({'success': True, 'status': status})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def get_available_port():
    with lock:
        available_ports = [port for port in range(Config.PORT_MIN, Config.PORT_MAX + 1) if port not in used_ports]
        
        if available_ports:
            selected_port = random.choice(available_ports)
            used_ports.add(selected_port)
            return selected_port
    return None

def cleanup_dead_sessions():
    print("[INFO] 正在清理无效的实验会话...")
    try:
        from utils.db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, user_id, vulnerability_id, docker_container_id FROM experiment_sessions WHERE end_time IS NULL'
        )
        sessions = cursor.fetchall()
        
        running_container_ids = set()
        success, stdout, _ = run_docker_command(
            "docker ps --format '{{.ID}}' 2>/dev/null",
            timeout=10
        )
        if success and stdout.strip():
            for line in stdout.strip().split('\n'):
                running_container_ids.add(line[:12])
        
        cleaned_count = 0
        for session in sessions:
            container_id = session.get('docker_container_id', '')
            # 只有当container_id不为空但容器不在运行时才清理
            # container_id为空表示用户只是开始了实验但还没启动容器，这是正常状态
            if container_id and container_id not in running_container_ids:
                print(f"[CLEANUP] 清理无效会话: id={session['id']}, container_id={container_id}")
                cursor.execute(
                    'UPDATE experiment_sessions SET end_time = NOW() WHERE id = %s',
                    (session['id'],)
                )
                cleaned_count += 1
        
        conn.commit()
        conn.close()
        print(f"[INFO] 共清理 {cleaned_count} 个无效会话")
    except Exception as e:
        print(f"[ERROR] 清理无效会话失败: {e}")

def restore_running_containers():
    print("[INFO] 正在从Docker恢复运行中的容器...")
    
    cleanup_dead_sessions()
    
    try:
        from utils.db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        success, stdout, _ = run_docker_command(
            "docker ps --format '{{.ID}}|{{.Names}}|{{.Ports}}|{{.Labels}}' 2>/dev/null",
            timeout=10
        )
        restored_count = 0
        removed_count = 0
        if success and stdout.strip():
            for line in stdout.strip().split('\n'):
                parts = line.split('|')
                if len(parts) >= 4:
                    container_id = parts[0][:12]
                    container_name = parts[1]
                    ports = parts[2]
                    
                    if container_name.startswith('mlaic_'):
                        port_match = re.search(r':(\d+)->', ports)
                        host_port = int(port_match.group(1)) if port_match else None
                        
                        cursor.execute(
                            'SELECT id, user_id, vulnerability_id, start_time FROM experiment_sessions WHERE docker_container_id = %s AND end_time IS NULL',
                            (container_id,)
                        )
                        session = cursor.fetchone()
                        
                        # 只有当数据库中有对应会话记录时才恢复容器
                        if session:
                            vulnerability_id = session.get('vulnerability_id')
                            user_id = session.get('user_id')
                            session_db_id = session.get('id')
                            start_time = session.get('start_time')
                            
                            cursor.execute('SELECT name FROM vulnerabilities WHERE id = %s', (vulnerability_id,))
                            vuln = cursor.fetchone()
                            vulnerability_name = vuln.get('name') if vuln else container_name
                            
                            timeout_at = None
                            if start_time:
                                import datetime
                                if isinstance(start_time, str):
                                    start_dt = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                                else:
                                    start_dt = start_time
                                timeout_dt = start_dt + datetime.timedelta(seconds=Config.EXPERIMENT_TIMEOUT)
                                timeout_at = timeout_dt.timestamp()
                            
                            container_info = {
                                'id': container_id,
                                'name': container_name,
                                'status': 'running',
                                'host_port': host_port,
                                'project_name': container_name,
                                'user_id': user_id,
                                'vulnerability_id': vulnerability_id,
                                'vulnerability_name': vulnerability_name,
                                'session_db_id': session_db_id,
                                'container_id': container_id,
                                'timeout_at': timeout_at
                            }
                            
                            with lock:
                                running_containers.append(container_info)
                                if host_port:
                                    used_ports.add(host_port)
                                if user_id:
                                    user_container_count[user_id] = user_container_count.get(user_id, 0) + 1
                            
                            restored_count += 1
                            print(f"[RESTORE] 恢复容器: {container_id}, user={user_id}, vuln={vulnerability_id}")
                        else:
                            # 数据库中没有对应会话记录，删除这个孤立的容器
                            print(f"[RESTORE] 删除孤立容器（无数据库会话）: {container_id}")
                            run_docker_command(f"docker rm -f {container_id}", timeout=15)
                            removed_count += 1
        
        conn.close()
        print(f"[INFO] 共恢复 {restored_count} 个容器")
    except Exception as e:
        print(f"[ERROR] 恢复容器失败: {e}")
