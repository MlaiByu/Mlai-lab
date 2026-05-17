from flask import Blueprint, jsonify, request, g
from utils.db import get_all_users, get_experiment_records, create_user, get_user_by_username, get_db_connection, get_user_by_id, get_experiment_sessions, get_all_vulnerabilities, hash_password
from utils.auth import teacher_or_admin_required, login_required

users_bp = Blueprint('users', __name__)

def get_record_status(record, running_sessions):
    if not record or record['attempt_count'] == 0:
        if running_sessions:
            return 'in_progress'
        return 'not_started'
    if record.get('success', 0) >= 1:
        return 'completed'
    if running_sessions:
        return 'in_progress'
    return 'attempted'

def get_running_sessions_for_user(user_id):
    sessions = get_experiment_sessions(user_id)
    running = {}
    for s in sessions:
        if s.get('end_time') is None and s.get('docker_container_id'):
            vuln_id = s.get('vulnerability_id')
            if vuln_id:
                running[vuln_id] = s
    return running

@users_bp.route('/api/users/list', methods=['GET'])
@teacher_or_admin_required
def get_users():
    users = get_all_users()
    vulnerabilities = get_all_vulnerabilities()
    result = []
    for user in users:
        records_dict = {r['vulnerability_id']: r for r in get_experiment_records(user['id'])}
        running_sessions = get_running_sessions_for_user(user['id'])

        exp_list = []
        for v in vulnerabilities:
            record = records_dict.get(v['id'])
            is_running = v['id'] in running_sessions
            exp_dict = {
                'vulnerability_id': v['id'],
                'name': v['name'],
                'category': v['category'],
                'attempt_count': record['attempt_count'] if record else 0,
                'success_count': record.get('success', 0) if record else 0,
                'success': record.get('success', 0) >= 1 if record else False,
                'status': get_record_status(record, is_running)
            }
            exp_list.append(exp_dict)

        total_attempts = sum(e['attempt_count'] for e in exp_list)
        total_success = sum(1 for e in exp_list if e['success'])

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
@login_required
def get_user_profile(user_id):
    try:
        if g.user_id != user_id and g.role not in ['admin', 'teacher']:
            return jsonify({"success": False, "message": "权限不足"}), 403
            
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({"success": False, "message": "用户不存在"})

        vulnerabilities = get_all_vulnerabilities()
        records_dict = {r['vulnerability_id']: r for r in get_experiment_records(user_id)}
        sessions = get_experiment_sessions(user_id)
        running_sessions = get_running_sessions_for_user(user_id)

        exp_details = []
        for v in vulnerabilities:
            record = records_dict.get(v['id'])
            is_running = v['id'] in running_sessions
            exp_details.append({
                'vulnerability_id': v['id'],
                'vulnerability_type': v['name'],
                'category': v['category'],
                'attempt_count': record['attempt_count'] if record else 0,
                'success_count': record.get('success', 0) if record else 0,
                'success': record.get('success', 0) >= 1 if record else False,
                'status': get_record_status(record, is_running),
                'last_attempt': record.get('first_success', '') if record else ''
            })

        total_attempts = sum(e['attempt_count'] for e in exp_details)
        total_success = sum(1 for e in exp_details if e['success'])
        total_vulns = len(vulnerabilities)

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
                    "completion_rate": round(total_success / total_vulns * 100, 1) if total_vulns > 0 else 0
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
@teacher_or_admin_required
def change_password(user_id):
    data = request.get_json()
    new_password = data.get('password', data.get('new_password', ''))

    if not new_password:
        return jsonify({"success": False, "message": "密码不能为空"})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({"success": False, "message": "用户不存在"})

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

@users_bp.route('/api/users/recent_completions', methods=['GET'])
def get_recent_completions():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.user_id, u.username, r.vulnerability_id, r.first_success, v.name
            FROM experiment_records r
            JOIN users u ON r.user_id = u.id
            LEFT JOIN vulnerabilities v ON r.vulnerability_id = v.id
            WHERE r.success >= 1 AND r.first_success IS NOT NULL
            ORDER BY r.first_success DESC
            LIMIT 10
        """)
        results = cursor.fetchall()
        conn.close()

        recent_completions = [{
            'user_id': r['user_id'],
            'username': r['username'],
            'vulnerability_id': r['vulnerability_id'],
            'name': r.get('name', ''),
            'first_success': r['first_success']
        } for r in results]

        return jsonify({"success": True, "data": recent_completions})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
