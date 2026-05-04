from flask import Blueprint, request, jsonify
from utils.db import (
    get_experiment_record,
    update_experiment_record,
    insert_experiment_record,
    get_experiment_records,
    create_experiment_session,
    update_experiment_session,
    delete_experiment_session,
    get_experiment_sessions,
    get_all_vulnerabilities,
    get_vulnerability_by_type
)
import datetime
import uuid

experiment_bp = Blueprint('experiment', __name__)

@experiment_bp.route('/api/experiment/start', methods=['POST'])
def start_experiment():
    data = request.get_json()
    user_id = data.get('user_id', data.get('userId', 0))
    vulnerability_type = data.get('vulnerability_type', data.get('vulnerabilityType', ''))
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    session_id = str(uuid.uuid4())
    create_experiment_session(user_id, vulnerability_type, session_id)

    record = get_experiment_record(user_id, vulnerability_type)
    if record:
        update_experiment_record(user_id, vulnerability_type, start_time=now, is_expired=0)
    else:
        insert_experiment_record(user_id, vulnerability_type, attempt_count=1, success_count=0, start_time=now, last_attempt=now, is_expired=0)

    return jsonify({"success": True, "message": "实验已开始", "startTime": now, "sessionId": session_id})

@experiment_bp.route('/api/experiment/complete', methods=['POST'])
def complete_experiment():
    data = request.get_json()
    user_id = data.get('user_id', data.get('userId', 0))
    experiment_key = data.get('experiment_key', data.get('experimentKey', ''))
    session_id = data.get('session_id', data.get('sessionId', None))
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    record = get_experiment_record(user_id, experiment_key)
    if record:
        record_success = record.get('success_count', 0)
        new_success = record_success + 1
        update_experiment_record(user_id, experiment_key,
            success_count=new_success,
            success=1,
            end_time=now,
            is_expired=1
        )
    else:
        insert_experiment_record(user_id, experiment_key, attempt_count=1, success_count=1, success=1, start_time=now, end_time=now, last_attempt=now, is_expired=0)

    if session_id:
        update_experiment_session(session_id, end_time=now, success=1)

    return jsonify({"success": True, "message": "实验完成"})

@experiment_bp.route('/api/experiment/records', methods=['GET'])
def get_experiment_records_route():
    user_id = request.args.get('userId', 0)
    records = get_experiment_records(user_id)
    now_dt = datetime.datetime.now()
    now_str = now_dt.strftime('%Y-%m-%d %H:%M')

    result = []
    for record in records:
        is_expired = bool(record.get('is_expired', 0))
        remaining_time = 0

        if not is_expired and record.get('start_time'):
            try:
                start_time = datetime.datetime.strptime(record['start_time'], '%Y-%m-%d %H:%M')
                elapsed = (now_dt - start_time).total_seconds()
                if elapsed > 3600 and record.get('success_count', 0) == 0:
                    is_expired = True
                    update_experiment_record(user_id, record['vulnerability_type'], is_expired=1, end_time=now_str)
                remaining_time = max(0, 3600 - elapsed)
            except:
                pass

        result.append({
            "vulnerability_type": record['vulnerability_type'],
            "attempt_count": record.get('attempt_count', 0),
            "success_count": record.get('success_count', 0),
            "success": record.get('success', 0),
            "last_attempt": record.get('last_attempt'),
            "first_success": record.get('first_success'),
            "total_time": round(float(record.get('total_time', 0)), 2),
            "start_time": record.get('start_time'),
            "end_time": record.get('end_time'),
            "remaining_time": round(remaining_time),
            "is_expired": is_expired
        })

    return jsonify({"success": True, "records": result})

@experiment_bp.route('/api/experiment/submit', methods=['POST'])
def submit_flag():
    data = request.get_json()
    user_id = data.get('user_id', data.get('userId', 0))
    vulnerability_type = data.get('vulnerability_type', '')
    flag = data.get('flag', '').strip()
    session_id = data.get('session_id', data.get('sessionId', None))
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    vuln = get_vulnerability_by_type(vulnerability_type)
    if not vuln:
        return jsonify({"success": False, "message": "未知的漏洞类型"})

    expected_flag = vuln['flag']
    success = flag == expected_flag

    if success:
        record = get_experiment_record(user_id, vulnerability_type)
        if session_id:
            update_experiment_session(session_id, end_time=now, success=1)
        if record:
            new_success = int(record.get('success_count', 0)) + 1
            update_experiment_record(user_id, vulnerability_type,
                success_count=new_success,
                success=1,
                end_time=now,
                is_expired=1
            )
        else:
            insert_experiment_record(user_id, vulnerability_type,
                attempt_count=1, success_count=1, success=1,
                start_time=now, end_time=now, last_attempt=now,
                is_expired=0
            )
        return jsonify({"success": True, "message": "Flag正确！挑战成功！"})
    else:
        return jsonify({"success": False, "message": "Flag错误，请重试"})

@experiment_bp.route('/api/experiment/solution', methods=['GET'])
def get_solution_route():
    vuln_type = request.args.get('type', '')
    vuln = get_vulnerability_by_type(vuln_type)
    solution = vuln['solution'] if vuln else '暂无解题思路'
    return jsonify({"success": True, "solution": solution})

@experiment_bp.route('/api/experiment/vulnerabilities', methods=['GET'])
def get_vulnerabilities_route():
    vulnerabilities = get_all_vulnerabilities()
    result = [{
        "id": vuln['id'],
        "vulnerability_type": vuln['vulnerability_type'],
        "description": vuln['description'],
        "difficulty": vuln['difficulty'],
        "category": vuln['category']
    } for vuln in vulnerabilities]

    return jsonify({"success": True, "vulnerabilities": result})

@experiment_bp.route('/api/experiment/sessions', methods=['GET'])
def get_experiment_sessions_route():
    user_id = request.args.get('userId', 0, type=int)
    vulnerability_type = request.args.get('vulnerabilityType', None)
    sessions = get_experiment_sessions(user_id, vulnerability_type)

    result = [{
        "id": session['id'],
        "session_id": session['session_id'],
        "vulnerability_type": session['vulnerability_type'],
        "start_time": session['start_time'],
        "end_time": session['end_time'],
        "success": session['success'] == 1,
        "status": "进行中" if session['end_time'] is None else ("成功" if session['success'] == 1 else "失败")
    } for session in sessions]

    return jsonify({"success": True, "sessions": result})

@experiment_bp.route('/api/experiment/end_session', methods=['POST'])
def end_session():
    data = request.get_json()
    session_id = data.get('session_id', data.get('sessionId', ''))
    success = data.get('success', False)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    if not session_id:
        return jsonify({"success": False, "message": "缺少session_id参数"}), 400

    update_experiment_session(session_id, end_time=now, success=1 if success else 0)
    return jsonify({"success": True, "message": "实验会话已结束"})
