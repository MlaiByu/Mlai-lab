from flask import request, jsonify, g
from functools import wraps
from routes.auth import verify_token

def _extract_and_verify_token():
    token = request.headers.get('Authorization')
    if not token:
        return None, jsonify({"success": False, "message": "请先登录"}), 401
    
    if token.startswith('Bearer '):
        token = token[7:]
    
    payload = verify_token(token)
    if not payload:
        return None, jsonify({"success": False, "message": "token无效或已过期"}), 401
    
    g.user_id = payload['user_id']
    g.username = payload['username']
    g.role = payload['role']
    return payload, None, None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        _, error, status = _extract_and_verify_token()
        if error:
            return error, status
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payload, error, status = _extract_and_verify_token()
        if error:
            return error, status
        
        if payload['role'] != 'admin':
            return jsonify({"success": False, "message": "需要管理员权限"}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def teacher_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payload, error, status = _extract_and_verify_token()
        if error:
            return error, status
        
        if payload['role'] not in ['admin', 'teacher']:
            return jsonify({"success": False, "message": "需要教师或管理员权限"}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def validate_input(input_string, allow_special=False):
    import re
    
    if not input_string or not isinstance(input_string, str):
        return False, "输入不能为空"
    
    if len(input_string) > 255:
        return False, "输入长度超过限制"
    
    if not allow_special:
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|EXEC|EXECUTE|XP_|SP_|0x)\b)",
            r"(\b(OR|AND)\s+(\d+)\s*=\s*(\d+))",
            r"(['\"])\s*OR\s*['\"]",
            r"(--|#|/\*|\*/)",
            r"(;|\\|`|\|)",
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                return False, "输入包含非法字符"
        
        xss_patterns = [
            r"(<script[^>]*>.*?</script>)",
            r"(<img[^>]*on\w+)",
            r"(javascript:)",
            r"(vbscript:)",
            r"(data:)",
            r"(<iframe[^>]*>)",
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                return False, "输入包含恶意脚本"
    
    return True, "验证通过"