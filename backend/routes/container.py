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
        timeout=120,
        env=env
    )
    if not success and 'docker compose' in stderr:
        success, stdout, stderr = run_docker_command(
            f"cd {docker_dir} && docker-compose -p {project_name} up -d",
            timeout=120,
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

def _async_remove(container_info):
    def _remove():
        cid = container_info.get('id')
        pn = container_info.get('project_name')
        dd = container_info.get('docker_dir')
        hp = container_info.get('host_port')
        uid = container_info.get('user_id')
        sid = container_info.get('session_id')
        use_compose = container_info.get('use_docker_compose', False)
        
        print(f"[CONTAINER] 开始删除容器: id={cid}, name={pn}, use_compose={use_compose}, docker_dir={dd}")
        
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
                if is_container_running(cid):
                    print(f"[CONTAINER] 强制删除容器: {cid}")
                    run_docker_command(f"docker rm -f {cid}", timeout=15)
            
            if pn:
                cleanup_docker_resources(pn)
            
        except Exception as e:
            print(f"[ERROR] 容器删除失败: {e}")
            try:
                if pn:
                    cleanup_docker_resources(pn)
                if cid:
                    run_docker_command(f"docker rm -f {cid}", timeout=10)
            except Exception as cleanup_e:
                print(f"[ERROR] 强制清理失败: {cleanup_e}")
        
        with lock:
            if cid:
                running_containers[:] = [c for c in running_containers if c.get('id') != cid]
            if pn:
                running_containers[:] = [c for c in running_containers if c.get('project_name') != pn]
            if hp:
                used_ports.discard(hp)
            decrement_user_container_count(uid)
        
        print(f"[CONTAINER] 容器删除完成: id={cid}, name={pn}")
        
        if uid and sid:
            try:
                from utils.db import update_experiment_session
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                update_experiment_session(sid, end_time=now, success=0)
            except Exception as e:
                print(f"[ERROR] 更新会话失败: {e}")
    
    threading.Thread(target=_remove, daemon=True).start()

def _create_container_sync(vulnerability_id, user_id, session_id):
    vulnerability_name, type_tag = _find_vulnerability_config(vulnerability_id)
    
    if not vulnerability_name or not type_tag:
        return None, '漏洞类型不存在'
    
    if get_user_container_count(user_id) >= Config.MAX_CONTAINERS_PER_USER:
        return None, '您当前已有一个运行中的实验，请先关闭当前实验再开启新实验'
    
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
        
        time.sleep(2)
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
        
        time.sleep(1)
    
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
        'session_id': session_id,
        'timeout_at': time.time() + Config.EXPERIMENT_TIMEOUT,
        'created_at': time.time()
    }
    
    with lock:
        running_containers.append(container_info)
        increment_user_container_count(user_id)
    
    return container_info, None

@container_bp.route('/api/container/create', methods=['POST'])
def create_container():
    try:
        data = request.get_json() if request.is_json else {}
        vulnerability_id = data.get('vulnerability_id', data.get('vulnerabilityId', 0))
        user_id = data.get('user_id', data.get('userId', 0))
        session_id = data.get('session_id', data.get('sessionId', ''))
        
        if not vulnerability_id:
            return jsonify({'success': False, 'message': '漏洞ID不能为空'}), 400
        
        container_info, error = _create_container_sync(vulnerability_id, user_id, session_id)
        
        if error:
            return jsonify({'success': False, 'message': error}), 500
        
        # 添加 container_id 字段以兼容前端
        container_info['container_id'] = container_info.get('id')
        
        return jsonify(container_info)
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@container_bp.route('/api/container/remove/<container_id>', methods=['POST'])
def remove_container(container_id):
    try:
        data = request.get_json() if request.is_json else {}
        user_id = data.get('user_id', data.get('userId', 0))
        session_id = data.get('session_id', data.get('sessionId', ''))
        
        container_info = None
        with lock:
            for c in running_containers:
                if c['id'] == container_id or c.get('name') == container_id:
                    container_info = c.copy()
                    break
        
        if not container_info:
            success, stdout, _ = run_docker_command(f"docker ps -q --no-trunc --filter name={container_id}", timeout=5)
            if not stdout.strip():
                return jsonify({'success': False, 'message': '容器不存在'}), 404
            
            container_info = {
                'id': container_id,
                'project_name': container_id,
                'user_id': user_id,
                'session_id': session_id
            }
        
        _async_remove(container_info)
        
        if session_id:
            try:
                from utils.db import update_experiment_session
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                update_experiment_session(session_id, end_time=now, success=0)
            except:
                pass
        
        return jsonify({'success': True, 'message': '容器删除任务已提交'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@container_bp.route('/api/container/list', methods=['GET'])
def list_containers():
    try:
        user_id = request.args.get('user_id', request.args.get('userId', 0))
        
        with lock:
            if user_id:
                containers = [c for c in running_containers if c.get('user_id') == int(user_id)]
            else:
                containers = list(running_containers)
        
        # 为每个容器添加 container_id 字段以兼容前端
        containers_with_id = []
        for c in containers:
            container = c.copy()
            container['container_id'] = container.get('id')
            containers_with_id.append(container)
        
        return jsonify({'success': True, 'containers': containers_with_id})
    
    except Exception as e:
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

def restore_running_containers():
    print("[INFO] 正在从Docker恢复运行中的容器...")
    try:
        success, stdout, _ = run_docker_command(
            "docker ps --format '{{.ID}}|{{.Names}}|{{.Ports}}|{{.Labels}}' 2>/dev/null",
            timeout=10
        )
        restored_count = 0
        if success and stdout.strip():
            for line in stdout.strip().split('\n'):
                parts = line.split('|')
                if len(parts) >= 4:
                    container_id = parts[0][:12]
                    container_name = parts[1]
                    ports = parts[2]
                    labels = parts[3]
                    
                    if container_name.startswith('mlaic_'):
                        port_match = re.search(r':(\d+)->', ports)
                        host_port = int(port_match.group(1)) if port_match else None
                        
                        container_info = {
                            'id': container_id,
                            'name': container_name,
                            'status': 'running',
                            'host_port': host_port,
                            'project_name': container_name
                        }
                        
                        with lock:
                            running_containers.append(container_info)
                            if host_port:
                                used_ports.add(host_port)
                        restored_count += 1
        
        print(f"[INFO] 共恢复 {restored_count} 个容器")
    except Exception as e:
        print(f"[ERROR] 恢复容器失败: {e}")