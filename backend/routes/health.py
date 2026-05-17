from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "service": "Mlai-Lab API",
        "version": "1.0.0"
    }), 200

@health_bp.route('/api/health/liveness', methods=['GET'])
def liveness_check():
    """存活检查接口"""
    return jsonify({"status": "alive"}), 200

@health_bp.route('/api/health/readiness', methods=['GET'])
def readiness_check():
    """就绪检查接口"""
    try:
        from utils.db import get_db_connection
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'ready', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'not_ready', 'error': str(e)}), 503
