from flask import Blueprint, request, jsonify
import uuid
import os
import time
import subprocess
import json
import datetime
from config import Config
import threading
import re

container_bp = Blueprint('container', __name__)

running_containers = []
used_ports = set()
port_cache = {'ports': set(), 'timestamp': 0}
PORT_CACHE_TTL = 5

lock = threading.Lock()

def get_cached_ports():
    current_time = time.time()
    if current_time - port_cache['timestamp'] < PORT_CACHE_TTL:
        return port_cache['ports'].copy()
    port_cache['ports'] = _scan_used_ports()
    port_cache['timestamp'] = current_time
    return port_cache['ports'].copy()

def _scan_used_ports():
    ports = set()
    try:
        result = subprocess.run(
            "ss -tlnp 2>/dev/null | awk 'NR>1{print $4}' | grep -oE '[0-9]+$'",
            shell=True, capture_output=True, text=True, timeout=2
        )
        for line in result.stdout.strip().split('\n'):
            if line.isdigit():
                ports.add(int(line))
    except:
        pass

    try:
        result = subprocess.run(
            "docker ps --format '{{.Ports}}' 2>/dev/null",
            shell=True, capture_output=True, text=True, timeout=5
        )
        for match in re.findall(r':(\d+)->', result.stdout):
            ports.add(int(match))
    except:
        pass

    return ports

def get_available_port():
    with lock:
        all_used = get_cached_ports()
        all_used.update(used_ports)
        for port in range(Config.PORT_MIN, Config.PORT_MAX + 1):
            if port not in all_used and port not in used_ports:
                used_ports.add(port)
                return port
        return None

tag_map = Config.DOCKER_VULN_MAP
docker_run_configs = Config.DOCKER_CONFIGS

def run_docker_command(cmd, timeout=30):
    try:
        proc = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return proc.returncode == 0, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, '', '命令执行超时'
    except Exception as e:
        return False, '', str(e)

def docker_compose_up(docker_dir, project_name, host_port):
    env_file = os.path.join(docker_dir, '.env')
    with open(env_file, 'w') as f:
        f.write(f"HOST_PORT={host_port}\n")

    success, stdout, stderr = run_docker_command(
        f"cd {docker_dir} && HOST_PORT={host_port} docker compose -p {project_name} up -d",
        timeout=120
    )
    return success, stdout, stderr

def docker_compose_down(docker_dir, project_name):
    return run_docker_command(
        f"cd {docker_dir} && docker compose -p {project_name} down",
        timeout=30
    )

def get_container_id_from_compose(docker_dir, project_name):
    for _ in range(3):
        success, stdout, _ = run_docker_command(
            f"cd {docker_dir} && docker compose -p {project_name} ps -q web",
            timeout=10
        )
        if success and stdout.strip():
            return stdout.strip()[:12]
        time.sleep(0.5)
    return None

def cleanup_expired_containers(user_id=None):
    expired = []
    current_time = time.time()
    for c in running_containers:
        if user_id and c.get('user_id') != user_id:
            continue
        if c.get('timeout_at') and current_time > c['timeout_at']:
            expired.append(c)
    for c in expired:
        _async_remove(c)

def _async_remove(container_info):
    def _remove():
        cid = container_info.get('id')
        pn = container_info.get('project_name')
        dd = container_info.get('docker_dir')
        hp = container_info.get('host_port')
        uid = container_info.get('user_id')
        vt = container_info.get('vulnerability_type')
        sid = container_info.get('session_id')

        if container_info.get('use_docker_compose') and pn and dd:
            docker_compose_down(dd, pn)
        elif cid:
            run_docker_command(f"docker rm -f {cid}", timeout=10)

        with lock:
            if cid:
                for c in running_containers:
                    if c['id'] == cid:
                        running_containers.remove(c)
                        break
            if hp:
                used_ports.discard(hp)

        if uid and vt:
            try:
                from utils.db import update_experiment_record, update_experiment_session
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                update_experiment_record(uid, vt, end_time=now, is_expired=1)
                if sid:
                    update_experiment_session(sid, end_time=now, success=0)
            except:
                pass

    threading.Thread(target=_remove, daemon=True).start()

@container_bp.route('/api/container/create', methods=['POST'])
def create_container():
    try:
        print(f"[DEBUG] create_container called at {datetime.datetime.now()}")
        data = request.get_json()
        print(f"[DEBUG] Data received: {data}")
        
        vulnerability_type = data.get('vulnerability_type')
        user_id = data.get('user_id', 0)
        session_id = data.get('session_id', '')

        if not vulnerability_type or not isinstance(vulnerability_type, str):
            return jsonify({'success': False, 'message': '漏洞类型无效'}), 400

        if vulnerability_type in ['SQL注入-中级', 'SQL注入-高级']:
            level = 'medium' if vulnerability_type == 'SQL注入-中级' else 'hard'
            return jsonify({
                'success': True,
                'container_id': f'sqli-lab-{level}',
                'container_name': f'sqli-lab-{level}',
                'host_port': 8000,
                'vulnerability_type': vulnerability_type,
                'lab_url': f'/api/sqli-lab/{level}',
                'message': 'SQL注入实验环境已就绪'
            })

        print(f"[DEBUG] Calling cleanup_expired_containers for user {user_id}")
        cleanup_expired_containers(user_id)
        print(f"[DEBUG] cleanup_expired_containers completed")

        type_tag = tag_map.get(vulnerability_type, vulnerability_type.lower().replace(' ', '-'))
        project_name = f"mlai-{type_tag[:8]}-{uuid.uuid4().hex[:6]}"
        docker_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docker', type_tag))
        print(f"[DEBUG] type_tag={type_tag}, docker_dir={docker_dir}")

        if not os.path.exists(docker_dir):
            return jsonify({'success': False, 'message': '漏洞环境不存在'}), 404

        print(f"[DEBUG] Calling get_available_port")
        host_port = get_available_port()
        print(f"[DEBUG] Got port: {host_port}")
        
        if not host_port:
            return jsonify({'success': False, 'message': '没有可用端口'}), 500

        config = docker_run_configs.get(vulnerability_type, {})
        print(f"[DEBUG] Config: {config}")
        use_compose = config.get('use_docker_compose', False)

        if use_compose:
            success, stdout, stderr = docker_compose_up(docker_dir, project_name, host_port)
            if not success:
                with lock:
                    used_ports.discard(host_port)
                return jsonify({'success': False, 'message': f'启动失败: {stderr}'}), 500

            container_id = get_container_id_from_compose(docker_dir, project_name)
            if not container_id:
                with lock:
                    used_ports.discard(host_port)
                docker_compose_down(docker_dir, project_name)
                return jsonify({'success': False, 'message': '容器启动超时'}), 500
        else:
            image = config.get('image', 'php:7.4-apache')
            container_port = config.get('port', 80)
            volumes = config.get('volumes', {})
            env_vars = config.get('env', {})
            cmd_extra = config.get('command', '')

            volume_str = ' '.join(f"-v {os.path.join(docker_dir, hp)}:{cp}" for hp, cp in volumes.items())
            env_str = ' '.join(f"-e {k}={v}" for k, v in env_vars.items())
            full_cmd = f"docker run -d --name {project_name} -p {host_port}:{container_port} {volume_str} {env_str} --label {Config.CONTAINER_LABEL}={vulnerability_type} --stop-timeout 10 {image} {cmd_extra}"

            success, stdout, stderr = run_docker_command(full_cmd, timeout=30)
            if not success:
                with lock:
                    used_ports.discard(host_port)
                return jsonify({'success': False, 'message': f'启动失败: {stderr}'}), 500
            container_id = stdout.strip()[:12]

        container_info = {
            'id': container_id,
            'name': project_name,
            'status': 'running',
            'vulnerability_type': vulnerability_type,
            'host_port': host_port,
            'use_docker_compose': use_compose,
            'project_name': project_name,
            'docker_dir': docker_dir,
            'user_id': user_id,
            'session_id': session_id,
            'timeout_at': time.time() + Config.EXPERIMENT_TIMEOUT
        }
        running_containers.append(container_info)

        return jsonify({
            'success': True,
            'container_id': container_id,
            'container_name': project_name,
            'host_port': host_port,
            'vulnerability_type': vulnerability_type,
            'message': '容器创建成功'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@container_bp.route('/api/container/remove/<container_id>', methods=['POST'])
def remove_container(container_id):
    try:
        data = request.get_json() if request.is_json else {}
        user_id = data.get('user_id', data.get('userId', 0))
        vulnerability_type = data.get('vulnerability_type', '')
        session_id = data.get('session_id', data.get('sessionId', ''))

        container_info = None
        for c in running_containers:
            if c['id'] == container_id or c.get('name') == container_id:
                container_info = c
                break

        if not container_info:
            success, stdout, _ = run_docker_command(f"docker ps -q --no-trunc --filter name={container_id}", timeout=5)
            if not stdout.strip():
                return jsonify({'success': False, 'message': '容器不存在'}), 404

        _async_remove(container_info)

        if user_id and vulnerability_type:
            try:
                from utils.db import update_experiment_record, update_experiment_session
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                update_experiment_record(user_id, vulnerability_type, end_time=now, is_expired=1)
                if session_id:
                    update_experiment_session(session_id, end_time=now, success=0)
            except:
                pass

        return jsonify({'success': True, 'container_id': container_id, 'message': '正在停止容器'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@container_bp.route('/api/container/status/<container_id>', methods=['GET'])
def get_container_status(container_id):
    for c in running_containers:
        if c['id'] == container_id:
            return jsonify({'success': True, 'status': c['status'], 'host_port': c.get('host_port')})
    success, stdout, _ = run_docker_command(f"docker inspect {container_id} --format '{{{{.State.Running}}}}'", timeout=5)
    return jsonify({'success': True, 'status': 'running' if stdout.strip() == 'true' else 'stopped'})

@container_bp.route('/api/container/list', methods=['GET'])
def list_containers():
    user_id = request.args.get('user_id', request.args.get('userId', 0))
    containers = [{
        'id': c['id'],
        'name': c['name'],
        'status': c['status'],
        'vulnerability_type': c['vulnerability_type'],
        'host_port': c.get('host_port')
    } for c in running_containers if user_id == 0 or c.get('user_id') == user_id]
    return jsonify({'success': True, 'containers': containers})

@container_bp.route('/api/container/get_by_vuln', methods=['POST'])
def get_container_by_vuln():
    try:
        data = request.get_json()
        vulnerability_type = data.get('vulnerability_type')
        user_id = data.get('user_id', 0)

        cleanup_expired_containers(user_id)

        for container in running_containers:
            if container.get('vulnerability_type') == vulnerability_type and container.get('user_id') == user_id:
                return jsonify({
                    'success': True,
                    'container_id': container.get('id'),
                    'container_name': container.get('name'),
                    'host_port': container.get('host_port'),
                    'vulnerability_type': container.get('vulnerability_type'),
                    'timeout_at': container.get('timeout_at')
                })

        return jsonify({'success': False, 'message': '没有找到运行中的容器'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@container_bp.route('/api/container/cleanup', methods=['POST'])
def cleanup_all():
    try:
        run_docker_command(f"docker rm -f $(docker ps -q --filter label={Config.CONTAINER_LABEL}) 2>/dev/null", timeout=30)
        running_containers.clear()
        used_ports.clear()
        return jsonify({'success': True, 'message': '已清理'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
