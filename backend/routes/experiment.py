from flask import Blueprint, request, jsonify
from utils.db import (
    get_experiment_record,
    update_experiment_record,
    insert_experiment_record,
    get_experiment_records,
    create_experiment_session,
    update_experiment_session,
    delete_experiment_session,
    get_experiment_sessions
)
import datetime
import uuid

experiment_bp = Blueprint('experiment', __name__)

EXPECTED_FLAGS = {
    'SQL注入-入门': 'Mlai{sqli_easy_2026_get_flag}',
    'SQL注入-中级': 'Mlai{sqli_medium_bypass_comment}',
    'SQL注入-高级': 'Mlai{sqli_hard_double_write_bypass}',
    '反射型XSS': 'Mlai{xss_reflected_flag}',
    '存储型XSS': 'Mlai{xss_stored_flag}',
    'DOM型XSS': 'Mlai{xss_dom_flag}',
    'PHP反序列化': 'Mlai{php_unserialize_flag}',
    'Python反序列化': 'Mlai{python_pickle_flag}'
}

SOLUTIONS = {
    'SQL注入-入门': '1. 这是一个简单的数字型SQL注入，无任何过滤\n2. 输入1\'测试，会发现SQL语法错误\n3. 使用UNION SELECT查询获取数据：1\' UNION SELECT 1,2,3,4,5,6,7,8,9,10--\n4. 查询flag表获取flag：1\' UNION SELECT 1,2,3,4,5,6,7,8,9,flag FROM flag--',
    'SQL注入-中级': '1. 这是一个字符型SQL注入，注释符被过滤\n2. 输入1\'测试，发现报错\n3. 由于注释符被过滤，需要闭合引号来绕过\n4. 可以使用payload：1\' union select 1,2,3,4,5,6,7,8,9,10 or \'1\'=\'1\n5. 查询flag：1\' union select 1,2,3,4,5,6,7,8,9,flag from flag or \'1\'=\'1',
    'SQL注入-高级': '1. 这是一个严格的SQL注入，过滤了多个关键字\n2. 常见的关键字如select、union等被过滤\n3. 可以使用双写绕过：selselectect、ununionion\n4. 双写绕过示例：1\' ununionion selselectect 1,2,3,4,5,6,7,8,9,10--\n5. 查询flag：1\' ununionion selselectect 1,2,3,4,5,6,7,8,9,flag frfromom flag--',
    '反射型XSS': '1. 这是一个简单的反射型XSS漏洞\n2. URL参数直接输出到页面中，没有过滤\n3. 测试：输入 <script>alert(1)</script>\n4. 尝试获取cookie：<script>alert(document.cookie)</script>',
    '存储型XSS': '1. 这是一个存储型XSS漏洞\n2. 用户输入会被存储到服务器\n3. 在输入框中输入恶意脚本并提交\n4. 刷新页面后，脚本会自动执行',
    'DOM型XSS': '1. 这是一个DOM型XSS漏洞\n2. 漏洞存在于前端JavaScript代码中\n3. 查看页面源码，找到处理用户输入的JavaScript\n4. 通常是通过location.hash或URL参数直接操作DOM',
    'PHP反序列化': '1. 这是一个PHP反序列化漏洞\n2. 程序会反序列化用户输入的数据\n3. 首先需要找到目标类的定义\n4. 构造恶意的序列化字符串\n5. 触发__wakeup或__destruct等魔术方法',
    'Python反序列化': '1. 这是一个Python pickle反序列化漏洞\n2. pickle模块是不安全的，不要反序列化不信任的数据\n3. 构造恶意的pickle数据\n4. 可以使用__reduce__方法执行任意命令',
    '文件上传': '1. 这是一个文件上传漏洞\n2. 尝试上传.php文件\n3. 如果有MIME类型检查，可以通过修改Content-Type绕过\n4. 如果有扩展名检查，可以尝试.php5、.php3或双重扩展名'
}

def update_or_insert_record(user_id, vulnerability_type, success, now):
    record = get_experiment_record(user_id, vulnerability_type)
    if record:
        update_experiment_record(
            user_id, vulnerability_type,
            success_count=int(record['success_count']) + success,
            attempt_count=int(record['attempt_count']) + 1,
            last_attempt=now,
            first_success=record['first_success'] or (now if success else None),
            total_time=float(record['total_time']) + 0.1
        )
    else:
        insert_experiment_record(
            user_id, vulnerability_type,
            attempt_count=1, success_count=success,
            last_attempt=now, first_success=now if success else None,
            total_time=0.1, start_time=now
        )

@experiment_bp.route('/api/experiment/start', methods=['POST'])
def start_experiment():
    data = request.get_json()
    user_id = data.get('user_id', data.get('userId', 0))
    vulnerability_type = data.get('experiment_key', data.get('vulnerabilityType', ''))
    now = datetime.datetime.now().isoformat()

    session_id = str(uuid.uuid4())
    create_experiment_session(user_id, vulnerability_type, session_id)

    record = get_experiment_record(user_id, vulnerability_type)
    if record:
        update_or_insert_record(user_id, vulnerability_type, 0, now)
    else:
        insert_experiment_record(user_id, vulnerability_type, attempt_count=1, success_count=0, start_time=now, last_attempt=now, is_expired=0)

    return jsonify({"success": True, "message": "实验已开始", "startTime": now, "sessionId": session_id})

@experiment_bp.route('/api/experiment/complete', methods=['POST'])
def complete_experiment():
    data = request.get_json()
    user_id = data.get('user_id', data.get('userId', 0))
    experiment_key = data.get('experiment_key', data.get('experimentKey', ''))
    session_id = data.get('session_id', data.get('sessionId', None))
    now = datetime.datetime.now().isoformat()

    record = get_experiment_record(user_id, experiment_key)
    success_count = int(record['success_count']) + 1 if record else 1
    total_count = int(record['attempt_count']) + 1 if record else 1

    update_or_insert_record(user_id, experiment_key, 1, now)
    if session_id:
        update_experiment_session(session_id, end_time=now, success=1)

    return jsonify({"success": True, "message": "实验完成", "successCount": success_count, "totalCount": total_count})

@experiment_bp.route('/api/experiment/records', methods=['GET'])
def get_experiment_records_route():
    user_id = request.args.get('userId', 0)
    records = get_experiment_records(user_id)
    now = datetime.datetime.now()

    result = []
    for record in records:
        is_expired = bool(record.get('is_expired', 0))
        remaining_time = 0

        if not is_expired and record['start_time']:
            try:
                elapsed = (now - datetime.datetime.fromisoformat(record['start_time'])).total_seconds()
                if elapsed > 3600 and record['success_count'] == 0:
                    is_expired = True
                    update_experiment_record(user_id, record['vulnerability_type'], is_expired=1)
                remaining_time = max(0, 3600 - elapsed)
            except:
                pass

        result.append({
            "vulnerability_type": record['vulnerability_type'],
            "attempt_count": record['attempt_count'],
            "success_count": record['success_count'],
            "last_attempt": record['last_attempt'],
            "first_success": record['first_success'],
            "total_time": round(float(record['total_time']), 2),
            "start_time": record['start_time'],
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
    now = datetime.datetime.now().isoformat()

    expected_flag = EXPECTED_FLAGS.get(vulnerability_type, 'CTF{default_flag}')
    success = flag == expected_flag

    if success:
        record = get_experiment_record(user_id, vulnerability_type)
        if record:
            update_experiment_record(user_id, vulnerability_type, success_count=int(record['success_count']) + 1)
        if session_id:
            update_experiment_session(session_id, end_time=now, success=1)
        update_experiment_record(user_id, vulnerability_type, is_expired=1)
        return jsonify({"success": True, "message": "Flag正确！挑战成功！"})
    else:
        return jsonify({"success": False, "message": "Flag错误，请重试"})

@experiment_bp.route('/api/experiment/solution', methods=['GET'])
def get_solution_route():
    vuln_type = request.args.get('type', '')
    solution = SOLUTIONS.get(vuln_type, '暂无解题思路')
    return jsonify({"success": True, "solution": solution})

@experiment_bp.route('/api/experiment/sessions', methods=['GET'])
def get_experiment_sessions_route():
    user_id = request.args.get('userId', 0)
    vulnerability_type = request.args.get('vulnerabilityType', None)
    sessions = get_experiment_sessions(user_id, vulnerability_type)

    result = [{
        "id": session['id'],
        "session_id": session['session_id'],
        "vulnerability_type": session['vulnerability_type'],
        "start_time": session['start_time'],
        "end_time": session['end_time'],
        "success": session['success'] == 1
    } for session in sessions]

    return jsonify({"success": True, "sessions": result})

@experiment_bp.route('/api/experiment/end_session', methods=['POST'])
def end_session():
    data = request.get_json()
    session_id = data.get('session_id', data.get('sessionId', ''))
    success = data.get('success', False)
    now = datetime.datetime.now().isoformat()

    if not session_id:
        return jsonify({"success": False, "message": "缺少session_id参数"}), 400

    update_experiment_session(session_id, end_time=now, success=1 if success else 0)
    return jsonify({"success": True, "message": "实验会话已结束"})
