from flask import Blueprint, jsonify
import psutil
import time

health_bp = Blueprint('health', __name__)

start_time = time.time()

@health_bp.route('/api/health')
def health_check():
    uptime = time.time() - start_time
    
    # 获取系统资源使用情况
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # 获取进程信息
    process = psutil.Process()
    process_cpu = process.cpu_percent()
    process_memory = process.memory_percent()
    
    return jsonify({
        'status': 'healthy',
        'uptime': {
            'seconds': int(uptime),
            'hours': round(uptime / 3600, 2)
        },
        'system': {
            'cpu_percent': cpu_percent,
            'memory_total': round(memory.total / (1024**3), 2),
            'memory_used': round(memory.used / (1024**3), 2),
            'memory_percent': memory.percent,
            'disk_total': round(disk.total / (1024**3), 2),
            'disk_used': round(disk.used / (1024**3), 2),
            'disk_percent': disk.percent
        },
        'process': {
            'cpu_percent': process_cpu,
            'memory_percent': process_memory,
            'pid': process.pid
        }
    })

@health_bp.route('/api/health/liveness')
def liveness_check():
    return jsonify({'status': 'alive'})

@health_bp.route('/api/health/readiness')
def readiness_check():
    try:
        from utils.db import get_db_connection
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'ready', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'not_ready', 'error': str(e)}), 503