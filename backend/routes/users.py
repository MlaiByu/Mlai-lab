from flask import Blueprint, jsonify, request
from utils.db import get_all_users, get_experiment_records, create_user, get_user_by_username, get_db_connection, hash_password, get_user_by_id, get_experiment_sessions
from datetime import datetime

users_bp = Blueprint('users', __name__)

def get_record_status(record):
    if record['attempt_count'] == 0:
        return 'not_started'
    return 'completed' if record['success_count'] > 0 else 'in_progress'

def calculate_total_time(sessions):
    total_seconds = 0.0
    for session in sessions:
        if session.get('start_time') and session.get('end_time'):
            try:
                start = datetime.fromisoformat(session['start_time'])
                end = datetime.fromisoformat(session['end_time'])
                total_seconds += (end - start).total_seconds()
            except:
                pass
    return round(total_seconds, 2)

@users_bp.route('/api/users/list', methods=['GET'])
def get_users():
    users = get_all_users()
    result = []
    for user in users:
        records = get_experiment_records(user['id'])
        sessions = get_experiment_sessions(user['id'])

        exp_list = []
        for r in records:
            vuln_sessions = [s for s in sessions if s['vulnerability_type'] == r['vulnerability_type']]
            exp_list.append({
                'vulnerability_type': r['vulnerability_type'],
                'attempt_count': r['attempt_count'],
                'success_count': r['success_count'],
                'last_attempt': r['last_attempt'],
                'total_time': calculate_total_time(vuln_sessions),
                'status': get_record_status(r)
            })

        result.append({
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'created_at': user['created_at'],
            'total_attempts': sum(r['attempt_count'] for r in records),
            'total_success': sum(r['success_count'] for r in records),
            'experiments': exp_list
        })

    return jsonify({"success": True, "data": result})

@users_bp.route('/api/users/create', methods=['POST'])
def create_user_api():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    role = data.get('role', 'student')

    if not username or not password:
        return jsonify({"success": False, "message": "用户名和密码不能为空"})

    if get_user_by_username(username):
        return jsonify({"success": False, "message": "用户名已存在"})

    create_user(username, password, role)
    return jsonify({"success": True, "message": "用户创建成功"})

@users_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM experiment_sessions WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM experiment_records WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "用户已删除"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@users_bp.route('/api/users/profile/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    try:
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({"success": False, "message": "用户不存在"})

        records = get_experiment_records(user_id)
        sessions = get_experiment_sessions(user_id)

        exp_details = []
        for record in records:
            vuln_sessions = [s for s in sessions if s['vulnerability_type'] == record['vulnerability_type']]
            total_time = calculate_total_time(vuln_sessions)

            exp_details.append({
                'vulnerability_type': record['vulnerability_type'],
                'attempt_count': record['attempt_count'],
                'success_count': record['success_count'],
                'first_success': record['first_success'],
                'last_attempt': record['last_attempt'],
                'total_time': total_time,
                'status': get_record_status(record),
                'session_count': len(vuln_sessions)
            })

        total_attempts = sum(r['attempt_count'] for r in records)
        total_success = sum(r['success_count'] for r in records)
        total_time_all = sum(float(r['total_time']) if r['total_time'] else 0 for r in exp_details)

        return jsonify({
            "success": True,
            "data": {
                "id": user['id'],
                "username": user['username'],
                "role": user['role'],
                "created_at": user['created_at'],
                "statistics": {
                    "total_attempts": total_attempts,
                    "total_success": total_success,
                    "total_time": round(total_time_all, 2),
                    "completion_rate": round(total_success / len(records) * 100, 1) if records else 0
                },
                "experiments": exp_details,
                "recent_sessions": [{
                    'session_id': s['session_id'],
                    'vulnerability_type': s['vulnerability_type'],
                    'start_time': s['start_time'],
                    'end_time': s['end_time'],
                    'success': s['success'] == 1
                } for s in sessions[:10]]
            }
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@users_bp.route('/api/users/change_password/<int:user_id>', methods=['POST'])
def change_password(user_id):
    data = request.get_json()
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return jsonify({"success": False, "message": "密码不能为空"})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({"success": False, "message": "用户不存在"})

        if hash_password(old_password) != result['password']:
            conn.close()
            return jsonify({"success": False, "message": "旧密码错误"})

        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hash_password(new_password), user_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "密码修改成功"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
