from flask import Blueprint, request, jsonify
import jwt
import datetime
from utils.db import get_user_by_username, create_user, hash_password

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = 'mlai-lab-secret-key'

def generate_token(user_id, username, role):
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({"success": False, "message": "用户名和密码不能为空"})
    
    if get_user_by_username(username):
        return jsonify({"success": False, "message": "用户名已存在"})
    
    create_user(username, password, 'student')
    
    return jsonify({"success": True, "message": "注册成功，默认角色为学生"})

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    user = get_user_by_username(username)
    
    if not user:
        return jsonify({"success": False, "message": "用户名或密码错误"})
    
    hashed_password = hash_password(password)
    
    if user['password'] == hashed_password:
        token = generate_token(user['id'], user['username'], user['role'])
        return jsonify({
            "success": True,
            "message": "登录成功",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "role": user['role'],
                "token": token
            }
        })
    else:
        return jsonify({"success": False, "message": "用户名或密码错误"})