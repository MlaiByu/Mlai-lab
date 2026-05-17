from flask import Blueprint, jsonify, request
from utils.db import get_all_users, get_experiment_records, create_user, get_user_by_username, get_db_connection, hash_password, get_user_by_id, get_experiment_sessions
from utils.auth import teacher_or_admin_required

users_bp = Blueprint('users', __name__)

def get_record_status(record):
    if record['attempt_count'] == 0:
        return 'not_started'
    return 'completed' if record.get('success', 0) == 1 else 'in_progress'

@users_bp.route('/api/users/list', methods=['GET'])
@teacher_or_admin_required
def get_users():
    users = get_all_users()
    result = []
    for user in users:
        records = get_experiment_records(user['id'])

        exp_list = []
        for r in records:
            exp_list.append({
                'vulnerability_id': r['vulnerability_id'],
                'name': r.get('name', ''),
                'category': r.get('category', ''),
                'attempt_count': r['attempt_count'],
                'success': r.get('success', 0) == 1,
                'status': get_record_status(r)
            })

        total_attempts = sum(r['attempt_count'] for r in records)
        total_success = sum(1 for r in records if r.get('success', 0) == 1)

        result.append({
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'score': user.get('score', 0),
            'created_at': user['created_at'],
            'total_attempts': total_attempts,
            'total_success': total_success,
            'experiments': exp_list
        })

    return jsonify({"success": True, "data": result})



@users_bp.route('/api/users/profile/<int:user_id>', methods=['GET'])
@teacher_or_admin_required
def get_user_profile(user_id):
    try:
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({"success": False, "message": "用户不存在"})

        records = get_experiment_records(user_id)
        sessions = get_experiment_sessions(user_id)

        exp_details = []
        for record in records:
            exp_details.append({
                'vulnerability_id': record['vulnerability_id'],
                'name': record.get('name', ''),
                'category': record.get('category', ''),
                'attempt_count': record['attempt_count'],
                'success': record.get('success', 0) == 1,
                'status': get_record_status(record)
            })

        total_attempts = sum(r['attempt_count'] for r in records)
        total_success = sum(1 for r in records if r.get('success', 0) == 1)

        return jsonify({
            "success": True,
            "data": {
                "id": user['id'],
                "username": user['username'],
                "role": user['role'],
                "score": user.get('score', 0),
                "created_at": user['created_at'],
                "statistics": {
                    "total_attempts": total_attempts,
                    "total_success": total_success,
                    "completion_rate": round(total_success / len(records) * 100, 1) if records else 0
                },
                "experiments": exp_details,
                "recent_sessions": [{
                    'session_id': s['session_id'],
                    'docker_container_id': s.get('docker_container_id'),
                    'server_port': s.get('server_port'),
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
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"success": False, "message": "请先登录"}), 401

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

@users_bp.route('/api/users/promote_to_teacher', methods=['POST'])
@teacher_or_admin_required
def promote_to_teacher():
    data = request.get_json()
    target_user_id = data.get('target_user_id', data.get('targetUserId', 0))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = %s", (target_user_id,))
        target_user = cursor.fetchone()
        if not target_user:
            conn.close()
            return jsonify({"success": False, "message": "目标用户不存在"})

        if target_user['role'] == 'admin':
            conn.close()
            return jsonify({"success": False, "message": "管理员角色不能被修改"})

        if target_user['role'] == 'teacher':
            conn.close()
            return jsonify({"success": False, "message": "该用户已是教师角色"})

        cursor.execute("UPDATE users SET role = 'teacher' WHERE id = %s", (target_user_id,))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": f"用户 {target_user['username']} 已提升为教师"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@users_bp.route('/api/users/demote_to_student', methods=['POST'])
@teacher_or_admin_required
def demote_to_student():
    data = request.get_json()
    target_user_id = data.get('target_user_id', data.get('targetUserId', 0))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = %s", (target_user_id,))
        target_user = cursor.fetchone()
        if not target_user:
            conn.close()
            return jsonify({"success": False, "message": "目标用户不存在"})

        if target_user['role'] == 'admin':
            conn.close()
            return jsonify({"success": False, "message": "管理员角色不能被修改"})

        if target_user['role'] == 'student':
            conn.close()
            return jsonify({"success": False, "message": "该用户已是学生角色"})

        cursor.execute("UPDATE users SET role = 'student' WHERE id = %s", (target_user_id,))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": f"用户 {target_user['username']} 已降为学生"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
