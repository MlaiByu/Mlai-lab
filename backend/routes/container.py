from flask import Blueprint, request, jsonify
import uuid
import os
import time
import subprocess
import json
import datetime

container_bp = Blueprint('container', __name__)

CONTAINER_LABEL = "mlai-lab-vulnerability"

running_containers = []

PORT_MIN = 10000
PORT_MAX = 13000

used_ports = set()

def get_available_port():
    for port in range(PORT_MIN, PORT_MAX + 1):
        if port in used_ports:
            continue
        result = subprocess.run(
            f"netstat -tlnp 2>/dev/null | grep :{port}",
            shell=True, capture_output=True, text=True
        )
        if result.returncode != 0:
            result_docker = subprocess.run(
                f"docker ps --format '{{{{.Ports}}}}' 2>/dev/null | grep -E ':{port}->'",
                shell=True, capture_output=True, text=True
            )
            if result_docker.returncode != 0:
                used_ports.add(port)
                return port
    return None

tag_map = {
    'SQL注入-入门': 'sqli-easy',
    'SQL注入-中级': 'sqli-medium',
    'SQL注入-高级': 'sqli-hard',
    '反射型XSS': 'xss-reflected',
    '存储型XSS': 'xss-stored',
    'DOM型XSS': 'xss-dom',
    'PHP反序列化': 'php-deserialization',
    'Python反序列化': 'python-deserialization',
    '文件上传': 'file-upload'
}

docker_run_configs = {
    'SQL注入-入门': {
        'use_docker_compose': True,
        'port': 80
    },
    'SQL注入-中级': {
        'use_docker_compose': True,
        'port': 80
    },
    'SQL注入-高级': {
        'use_docker_compose': True,
        'port': 80
    },
    '反射型XSS': {
        'use_docker_compose': True,
        'port': 80
    },
    '存储型XSS': {
        'use_docker_compose': True,
        'port': 80
    },
    'DOM型XSS': {
        'use_docker_compose': True,
        'port': 80
    },
    'PHP反序列化': {
        'image': 'php:7.4-apache',
        'port': 80,
        'volumes': {'./www': '/var/www/html'},
        'env': {}
    },
    'Python反序列化': {
        'image': 'python:3.9-slim',
        'port': 8000,
        'volumes': {'./www': '/app'},
        'command': 'python server.py',
        'env': {}
    },
    '文件上传': {
        'image': 'php:7.4-apache',
        'port': 80,
        'volumes': {'./www': '/var/www/html'},
        'env': {}
    }
}

def run_docker_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, '', str(e)

def cleanup_expired_containers(user_id=None):
    expired_containers = []
    for c in running_containers:
        if user_id and c.get('user_id') != user_id:
            continue
        try:
            start_time = datetime.datetime.fromisoformat(c.get('created_at', ''))
            now = datetime.datetime.now()
            elapsed = (now - start_time).total_seconds()
            if elapsed > 3600:
                expired_containers.append(c)
        except:
            pass

    for c in expired_containers:
        container_id = c.get('id')
        if container_id:
            if c.get('use_docker_compose'):
                project_name = c.get('project_name')
                docker_dir = c.get('docker_dir')
                if project_name and docker_dir:
                    run_docker_command(
                        f"cd {docker_dir} && docker compose -p {project_name} down -v"
                    )
            else:
                run_docker_command(f"docker rm -f {container_id}")

        host_port = c.get('host_port')
        if host_port and host_port in used_ports:
            used_ports.discard(host_port)

        if c in running_containers:
            running_containers.remove(c)

def cleanup_all_containers():
    containers_to_remove = running_containers.copy()

    for c in containers_to_remove:
        container_id = c.get('id')
        if container_id:
            if c.get('use_docker_compose'):
                project_name = c.get('project_name')
                docker_dir = c.get('docker_dir')
                if project_name and docker_dir:
                    run_docker_command(
                        f"cd {docker_dir} && docker compose -p {project_name} down -v"
                    )
            else:
                run_docker_command(f"docker rm -f {container_id}")

        host_port = c.get('host_port')
        if host_port and host_port in used_ports:
            used_ports.discard(host_port)

        if c in running_containers:
            running_containers.remove(c)

@container_bp.route('/api/container/create', methods=['POST'])
def create_container():
    try:
        data = request.get_json()
        vulnerability_type = data.get('vulnerability_type')
        user_id = data.get('user_id', 0)
        session_id = data.get('session_id', '')

        if not vulnerability_type:
            return jsonify({'success': False, 'message': '漏洞类型不能为空'}), 400

        if not isinstance(vulnerability_type, str):
            return jsonify({'success': False, 'message': '漏洞类型必须是字符串'}), 400

        cleanup_expired_containers(user_id)

        type_tag = tag_map.get(vulnerability_type, vulnerability_type.lower().replace(' ', '-'))
        project_name = f"mlai-lab-{type_tag}-{uuid.uuid4().hex[:8]}"

        success_docker, stdout_docker, stderr_docker = run_docker_command("docker info")
        if not success_docker:
            return jsonify({'success': False, 'message': 'Docker服务不可用'}), 500

        docker_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docker', type_tag))

        host_port = get_available_port()
        if not host_port:
            return jsonify({'success': False, 'message': '端口范围内没有可用端口'}), 500

        config = docker_run_configs.get(vulnerability_type, {})

        if config.get('use_docker_compose'):
            env_file = os.path.join(docker_dir, '.env')
            with open(env_file, 'w') as f:
                f.write(f"HOST_PORT={host_port}\n")

            cmd = f"cd {docker_dir} && HOST_PORT={host_port} docker compose -p {project_name} up -d"
            success_run, stdout_run, stderr_run = run_docker_command(cmd)

            if not success_run:
                return jsonify({'success': False, 'message': f'启动容器失败: {stderr_run}'}), 500

            time.sleep(5)

            success_ps, stdout_ps, stderr_ps = run_docker_command(
                f"cd {docker_dir} && docker compose -p {project_name} ps -q web"
            )

            if not success_ps or not stdout_ps.strip():
                return jsonify({'success': False, 'message': '获取容器ID失败'}), 500

            container_id = stdout_ps.strip()[:12]

            container_info = {
                'id': container_id,
                'name': project_name,
                'status': 'running',
                'vulnerability_type': vulnerability_type,
                'host_port': host_port,
                'use_docker_compose': True,
                'project_name': project_name,
                'docker_dir': docker_dir,
                'user_id': user_id,
                'session_id': session_id,
                'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'timeout_at': time.time() + 3600
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
        else:
            image = config.get('image', 'php:7.4-apache')
            container_port = config.get('port', 80)
            volumes = config.get('volumes', {})
            env_vars = config.get('env', {})
            command = config.get('command', '')

            volume_str = ""
            for host_path, container_path in volumes.items():
                abs_host_path = os.path.join(docker_dir, host_path)
                volume_str += f"-v {abs_host_path}:{container_path} "

            env_str = ""
            for key, value in env_vars.items():
                env_str += f"-e {key}={value} "

            stop_timeout = 3600

            container_name = project_name
            cmd = f"docker run -d --name {container_name} -p {host_port}:{container_port} {volume_str}{env_str}--label {CONTAINER_LABEL}={vulnerability_type} --stop-timeout {stop_timeout} {image}"

            if command:
                cmd = cmd + f" {command}"

            success_run, stdout_run, stderr_run = run_docker_command(cmd)

            if not success_run:
                return jsonify({'success': False, 'message': f'启动容器失败: {stderr_run}'}), 500

            container_id = stdout_run.strip()[:12]
            time.sleep(2)

            container_info = {
                'id': container_id,
                'name': container_name,
                'status': 'running',
                'vulnerability_type': vulnerability_type,
                'host_port': host_port,
                'user_id': user_id,
                'session_id': session_id,
                'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'timeout_at': time.time() + 3600
            }
            running_containers.append(container_info)

            return jsonify({
                'success': True,
                'container_id': container_id,
                'container_name': container_name,
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
            if c['id'] == container_id:
                if c.get('user_id') != user_id:
                    return jsonify({'success': False, 'message': '您没有权限删除此容器'}), 403
                container_info = c
                break

        if not container_info:
            return jsonify({'success': False, 'message': '容器不存在'}), 404

        if container_info.get('use_docker_compose'):
            project_name = container_info.get('project_name')
            docker_dir = container_info.get('docker_dir')
            if project_name and docker_dir:
                success, stdout, stderr = run_docker_command(
                    f"cd {docker_dir} && docker compose -p {project_name} down -v"
                )
        else:
            success, stdout, stderr = run_docker_command(f"docker rm -f {container_id}")

        if success:
            for c in running_containers:
                if c['id'] == container_id:
                    host_port = c.get('host_port')
                    if host_port and host_port in used_ports:
                        used_ports.discard(host_port)
                    if c in running_containers:
                        running_containers.remove(c)
                    break

            if user_id and vulnerability_type:
                try:
                    from utils.db import update_experiment_record, update_experiment_session
                    import datetime
                    update_experiment_record(user_id, vulnerability_type, is_expired=1)
                    if session_id:
                        now = datetime.datetime.now().isoformat()
                        update_experiment_session(session_id, end_time=now, success=0)
                except Exception as e:
                    pass

            return jsonify({
                'success': True,
                'container_id': container_id,
                'message': '容器已删除'
            })
        else:
            return jsonify({'success': False, 'message': stderr}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@container_bp.route('/api/container/get_by_vuln', methods=['POST'])
def get_container_by_vuln():
    data = request.get_json()
    vulnerability_type = data.get('vulnerability_type')
    user_id = data.get('user_id', 0)

    if not vulnerability_type:
        return jsonify({'success': False, 'message': '漏洞类型不能为空'}), 400

    try:
        for c in running_containers:
            if c['vulnerability_type'] == vulnerability_type and c['status'] == 'running' and c.get('user_id') == user_id:
                if c.get('timeout_at') and time.time() >= c.get('timeout_at'):
                    cleanup_expired_containers(user_id)
                    return jsonify({'success': False, 'message': '容器已过期'})

                return jsonify({
                    'success': True,
                    'container_id': c['id'],
                    'container_name': c['name'],
                    'host_port': c['host_port'],
                    'vulnerability_type': c['vulnerability_type'],
                    'timeout_at': c.get('timeout_at'),
                    'status': c['status']
                })

        return jsonify({'success': False, 'message': '没有运行中的容器'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@container_bp.route('/api/container/cleanup_all', methods=['POST'])
def cleanup_all_containers_route():
    try:
        cleanup_all_containers()
        return jsonify({'success': True, 'message': '所有容器已清理'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500