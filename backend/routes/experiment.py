from flask import Blueprint, request, jsonify
from utils.db import (
    get_experiment_record,
    update_experiment_record,
    insert_experiment_record,
    get_experiment_records,
    create_experiment_session,
    update_experiment_session,
    get_experiment_sessions,
    get_all_vulnerabilities,
    get_vulnerability_by_id,
    add_user_score
)
import datetime
import uuid

experiment_bp = Blueprint('experiment', __name__)

@experiment_bp.route('/api/experiment/start', methods=['POST'])
def start_experiment():
    data = request.get_json()
    user_id = data.get('user_id', data.get('userId', 0))
    vulnerability_id = data.get('vulnerability_id', data.get('vulnerabilityId', 0))
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    session_db_id, session_uuid = create_experiment_session(user_id, vulnerability_id=vulnerability_id)

    record = get_experiment_record(user_id, vulnerability_id)
    if record:
        new_attempt = record.get('attempt_count', 0) + 1
        update_experiment_record(user_id, vulnerability_id, attempt_count=new_attempt)
    else:
        insert_experiment_record(user_id, vulnerability_id, attempt_count=1, success_count=0)

    return jsonify({"success": True, "message": "实验已开始", "startTime": now, "sessionId": session_uuid})

@experiment_bp.route('/api/experiment/submit', methods=['POST'])
def submit_flag():
    data = request.get_json()
    user_id = data.get('user_id', data.get('userId', 0))
    vulnerability_id = data.get('vulnerability_id', data.get('vulnerabilityId', 0))
    flag = data.get('flag', '').strip()
    session_db_id = data.get('session_db_id', data.get('sessionDbId', None))
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    vuln = get_vulnerability_by_id(vulnerability_id)
    if not vuln:
        return jsonify({"success": False, "message": "未知的漏洞类型"})

    expected_flag = vuln['flag']
    success = flag == expected_flag

    if success:
        record = get_experiment_record(user_id, vulnerability_id)
        is_first_success = False
        
        if session_db_id:
            update_experiment_session(session_db_id, end_time=now, success=1)
        else:
            sessions = get_experiment_sessions(user_id)
            target_session = None
            for s in sessions:
                if s.get('vulnerability_id') == vulnerability_id and s.get('success') == 0:
                    if not target_session or s.get('start_time', '') > target_session.get('start_time', ''):
                        target_session = s
            if target_session:
                update_experiment_session(target_session.get('id'), end_time=now, success=1)
        
        if record:
            current_success = record.get('success_count', 0)
            new_success = current_success + 1
            if current_success == 0:
                is_first_success = True
            update_experiment_record(user_id, vulnerability_id, success_count=new_success)
        else:
            insert_experiment_record(user_id, vulnerability_id, attempt_count=1, success_count=1)
            is_first_success = True
        
        if is_first_success:
            add_user_score(user_id, 100)
        
        return jsonify({"success": True, "message": "Flag正确！挑战成功！" + (" +100分" if is_first_success else "")})
    else:
        return jsonify({"success": False, "message": "Flag错误，请重试"})

@experiment_bp.route('/api/experiment/vulnerabilities', methods=['GET'])
def get_vulnerabilities_route():
    vulnerabilities = get_all_vulnerabilities()
    result = [{
        "id": vuln['id'],
        "name": vuln['name'],
        "category": vuln['category']
    } for vuln in vulnerabilities]

    return jsonify({"success": True, "vulnerabilities": result})

@experiment_bp.route('/api/experiment/end_session', methods=['POST'])
def end_session():
    data = request.get_json()
    session_db_id = data.get('session_db_id', data.get('sessionDbId', 0))
    success = data.get('success', False)
    user_id = data.get('user_id', data.get('userId', 0))
    vulnerability_id = data.get('vulnerability_id', data.get('vulnerabilityId', 0))
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if session_db_id:
        update_experiment_session(session_db_id, end_time=now, success=1 if success else 0)
    elif user_id and vulnerability_id and success:
        sessions = get_experiment_sessions(user_id)
        target_session = None
        for s in sessions:
            if s.get('vulnerability_id') == vulnerability_id and s.get('success') == 0:
                if not target_session or s.get('start_time', '') > target_session.get('start_time', ''):
                    target_session = s
        if target_session:
            update_experiment_session(target_session.get('id'), end_time=now, success=1)

    return jsonify({"success": True, "message": "实验会话已结束"})

@experiment_bp.route('/api/experiment/records/<int:user_id>', methods=['GET'])
def get_experiment_records_route(user_id):
    records = get_experiment_records(user_id)
    result = [{
        'vulnerability_id': r['vulnerability_id'],
        'name': r.get('name', ''),
        'category': r.get('category', ''),
        'attempt_count': r['attempt_count'],
        'success_count': r.get('success_count', 0),
        'success': r.get('success_count', 0) >= 1
    } for r in records]
    return jsonify({"success": True, "records": result})
