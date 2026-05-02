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

def run_docker_command(cmd):
    try:
        cmd = cmd.replace('/root/.local/bin/docker-compose', 'docker compose')
        cmd = cmd.replace('docker-compose', 'docker compose')

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
            start_time = datetime.datetime.fromisoformat(c.get('start_time', ''))
            now = datetime.datetime.now()
            elapsed = (now - start_time).total_seconds()
            if elapsed > 3600:
                expired_containers.append(c)
        except:
            pass
    
    for c in expired_containers:
        compose_dir = c.get('compose_dir')
        if compose_dir and os.path.exists(compose_dir):
            run_docker_command(f"cd {compose_dir} && docker compose down")
        else:
            run_docker_command(f"docker rm -f {c['id']}")
        
        for i, container in enumerate(running_containers):
            if container['id'] == c['id']:
                del running_containers[i]
                break

@container_bp.route('/api/container/create', methods=['POST'])
def create_container():
    try:
        data = request.json
        vulnerability_type = data.get('vulnerability_type')
        user_id = data.get('user_id', 0)
        
        if not vulnerability_type:
            return jsonify({'success': False, 'message': '漏洞类型不能为空'}), 400
        
        if not isinstance(vulnerability_type, str):
            return jsonify({'success': False, 'message': '漏洞类型必须是字符串'}), 400
        
        cleanup_expired_containers(user_id)
        
        type_tag = tag_map.get(vulnerability_type, vulnerability_type.lower().replace(' ', '-'))
        container_name = f"mlai-lab-{type_tag}-{uuid.uuid4().hex[:8]}"
        
        success_docker, stdout_docker, stderr_docker = run_docker_command("docker info")
        if not success_docker:
            return jsonify({'success': False, 'message': 'Docker服务不可用'}), 500
        
        docker_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docker', type_tag))
        compose_file = os.path.join(docker_dir, 'docker-compose.yml')
        
        host_port = get_available_port()
        if not host_port:
            return jsonify({'success': False, 'message': '端口范围内没有可用端口'}), 500
        
        if os.path.exists(compose_file):
            _, _, _ = run_docker_command(f"cd {docker_dir} && docker compose down 2>/dev/null")
            
            cmd = f"cd {docker_dir} && HOST_PORT={host_port} docker compose up -d --build"
            success_build, stdout_build, stderr_build = run_docker_command(cmd)
            if not success_build:
                return jsonify({'success': False, 'message': f'启动容器失败: {stderr_build}'}), 500
            
            time.sleep(3)
            
            success_ps, stdout_ps, stderr_ps = run_docker_command(
                f"cd {docker_dir} && docker compose ps -q web"
            )
            if success_ps and stdout_ps:
                container_id = stdout_ps.strip()[:12]
            else:
                success_ps, stdout_ps, stderr_ps = run_docker_command(
                    f"docker ps --filter name=*{type_tag}* --format '{{.ID}}'"
                )
                if not success_ps or not stdout_ps:
                    return jsonify({'success': False, 'message': '无法获取容器信息'}), 500
                container_id = stdout_ps.strip().split('\n')[0][:12]
            
            if not container_id:
                return jsonify({'success': False, 'message': '无法获取容器信息'}), 500
            
            image_tag = f"mlai-lab-{type_tag}"
        else:
            image_tag = f"mlai-lab-{type_tag}"
            
            success_img, stdout_img, stderr_img = run_docker_command(f"docker images -q {image_tag}")
            if not success_img or not stdout_img:
                return jsonify({'success': False, 'message': '镜像不存在'}), 500
            
            success_run, stdout_run, stderr_run = run_docker_command(
                f"docker run -d --name {container_name} -p {host_port}:80 --label {CONTAINER_LABEL}={vulnerability_type} --user 1000 --stop-timeout 3600 {image_tag}"
            )
            
            if not success_run:
                return jsonify({'success': False, 'message': f'启动容器失败: {stderr_run}'}), 500
            
            container_id = stdout_run
            
            time.sleep(2)
        
        container_info = {
            'id': container_id,
            'name': container_name,
            'status': 'running',
            'vulnerability_type': vulnerability_type,
            'host_port': host_port,
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'timeout_at': time.time() + 3600,
            'compose_dir': docker_dir if os.path.exists(compose_file) else None
        }
        running_containers.append(container_info)
        
        return jsonify({
            'success': True,
            'container_id': container_id,
            'container_name': container_name,
            'host_port': host_port,
            'vulnerability_type': vulnerability_type,
            'image': image_tag,
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
        
        compose_dir = None
        vuln_type = None
        for c in running_containers:
            if c['id'] == container_id:
                compose_dir = c.get('compose_dir')
                vuln_type = c.get('vulnerability_type')
                break
        
        if compose_dir and os.path.exists(compose_dir):
            success, stdout, stderr = run_docker_command(f"cd {compose_dir} && docker compose down")
        else:
            success, stdout, stderr = run_docker_command(f"docker rm -f {container_id}")
        
        if success:
            for i, c in enumerate(running_containers):
                if c['id'] == container_id:
                    host_port = c.get('host_port')
                    if host_port and host_port in used_ports:
                        used_ports.remove(host_port)
                    del running_containers[i]
                    break
            
            if user_id and vulnerability_type:
                try:
                    from utils.db import update_experiment_record, delete_experiment_session
                    update_experiment_record(user_id, vulnerability_type, is_expired=1)
                    if session_id:
                        delete_experiment_session(session_id)
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
    data = request.json
    vulnerability_type = data.get('vulnerability_type')
    if not vulnerability_type:
        return jsonify({'success': False, 'message': '漏洞类型不能为空'}), 400
    try:
        for c in running_containers:
            if c['vulnerability_type'] == vulnerability_type and c['status'] == 'running':
                if c.get('timeout_at') and time.time() >= c['timeout_at']:
                    if c.get('compose_dir') and os.path.exists(c['compose_dir']):
                        run_docker_command(f"cd {c['compose_dir']} && docker compose down")
                    else:
                        run_docker_command(f"docker rm -f {c['id']}")
                    
                    for i, container in enumerate(running_containers):
                        if container['id'] == c['id']:
                            del running_containers[i]
                            break
                    
                    return jsonify({'success': False, 'message': '容器已过期'})
                
                return jsonify({
                    'success': True,
                    'container_id': c['id'],
                    'container_name': c['name'],
                    'host_port': c['host_port'],
                    'vulnerability_type': c['vulnerability_type'],
                    'timeout_at': c['timeout_at'],
                    'status': c['status']
                })
        
        success, stdout, stderr = run_docker_command(
            f"docker ps --filter label={CONTAINER_LABEL}={vulnerability_type} --format '{{.ID}} {{.Ports}}'"
        )
        
        if success and stdout:
            lines = stdout.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    container_id = parts[0]
                    ports = ' '.join(parts[1:])
                    if '0.0.0.0:' in ports and '->80/tcp' in ports:
                        host_port = ports.split('0.0.0.0:')[1].split('->')[0].strip()
                        
                        success_name, stdout_name, stderr_name = run_docker_command(
                            f"docker inspect --format '{{.Name}}' {container_id}"
                        )
                        container_name = stdout_name.strip().lstrip('/') if success_name else f"container-{container_id[:8]}"
                        
                        return jsonify({
                            'success': True,
                            'container_id': container_id,
                            'container_name': container_name,
                            'host_port': host_port,
                            'vulnerability_type': vulnerability_type,
                            'timeout_at': time.time() + 3600,
                            'status': 'running'
                        })
        
        return jsonify({'success': False, 'message': '没有运行中的容器'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
