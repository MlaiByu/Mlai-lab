from flask import Blueprint, request, jsonify, render_template_string
import pymysql
import re

sqli_lab_bp = Blueprint('sqli_lab', __name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>SQL注入靶场 - {{ title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, {{ gradient_start }} 0%, {{ gradient_end }} 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            width: 400px;
        }
        .login-container h2 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 24px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: bold;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            border-color: {{ gradient_start }};
            outline: none;
        }
        .btn-login {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, {{ gradient_start }} 0%, {{ gradient_end }} 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn-login:hover {
            transform: translateY(-2px);
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
        }
        .result.success {
            background: #d4edda;
            color: #155724;
        }
        .result.error {
            background: #f8d7da;
            color: #721c24;
        }
        .sql-display {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            font-family: monospace;
            font-size: 12px;
            color: #333;
            word-break: break-all;
        }
        .sql-label {
            font-weight: bold;
            color: {{ gradient_start }};
            margin-bottom: 5px;
            display: block;
        }
        .info {
            margin-top: 20px;
            padding: 10px;
            background: #fff3cd;
            border-radius: 8px;
            font-size: 12px;
            color: #856404;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>用户登录</h2>

        <form method="GET" action="">
            <div class="form-group">
                <label for="username">用户名</label>
                <input type="text" id="username" name="username" placeholder="请输入用户名" value="{{ username }}">
            </div>

            <div class="form-group">
                <label for="password">密码</label>
                <input type="password" id="password" name="password" placeholder="请输入密码" value="{{ password }}">
            </div>

            <button type="submit" class="btn-login">登录</button>
        </form>

        {% if result %}
        <div class="result {{ result_type }}">{{ result }}</div>
        {% endif %}

        {% if sql %}
        <div class="sql-display">
            <span class="sql-label">执行的SQL语句：</span>
            {{ sql }}
        </div>
        {% endif %}

        {% if info %}
        <div class="info">{{ info }}</div>
        {% endif %}
    </div>
</body>
</html>
'''

def get_db_connection():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='mlai2024',
            database='sqli_lab',
            charset='utf8mb4'
        )
        return conn
    except:
        return None

def init_sqli_lab_db():
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS sqli_lab")
        cursor.execute("USE sqli_lab")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                password VARCHAR(50)
            )
        ''')
        
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
            cursor.execute("INSERT INTO users (username, password) VALUES ('test', 'test123')")
            cursor.execute("INSERT INTO users (username, password) VALUES ('guest', 'guest123')")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flag (
                id INT AUTO_INCREMENT PRIMARY KEY,
                flag VARCHAR(100)
            )
        ''')
        
        cursor.execute("SELECT COUNT(*) FROM flag")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO flag (flag) VALUES ('Mlai{sqli_medium_bypass_comment}')")
        
        conn.commit()
        return True
    except Exception as e:
        print(f"初始化数据库失败: {e}")
        return False
    finally:
        conn.close()

@sqli_lab_bp.route('/api/sqli-lab/<level>', methods=['GET'])
def sqli_lab(level):
    username = request.args.get('username', '')
    password = request.args.get('password', '')
    
    result = None
    result_type = None
    sql_query = None
    info = None
    
    if level == 'medium':
        title = '中级'
        gradient_start = '#f39c12'
        gradient_end = '#e74c3c'
    elif level == 'hard':
        title = '高级'
        gradient_start = '#e74c3c'
        gradient_end = '#c0392b'
    else:
        title = '入门'
        gradient_start = '#3498db'
        gradient_end = '#2980b9'
    
    if username and password:
        init_sqli_lab_db()
        conn = get_db_connection()
        
        if not conn:
            return render_template_string(HTML_TEMPLATE,
                                         title=title,
                                         gradient_start=gradient_start,
                                         gradient_end=gradient_end,
                                         username=username,
                                         password=password,
                                         result='数据库连接失败',
                                         result_type='error')
        
        try:
            cursor = conn.cursor()
            
            if level == 'medium':
                username_filtered = username.replace('--', '').replace('#', '').replace('/*', '')
                info = '提示：注释符(#、--、/*)已被过滤'
            elif level == 'hard':
                keywords = ['select', 'union', 'or', 'and', 'order', 'by', 'where', 'from', 'database', 'information_schema', 'group_concat', 'column', 'table']
                username_filtered = username
                for keyword in keywords:
                    username_filtered = re.sub(keyword, '', username_filtered, flags=re.IGNORECASE)
                info = '提示：常见关键字已被过滤（select、union、or、and、order、by、where、from等）'
            else:
                username_filtered = username
                info = '提示：这是一个简单的SQL注入漏洞'
            
            sql = f"SELECT * FROM users WHERE username = '{username_filtered}' AND password = '{password}'"
            sql_query = sql
            
            cursor.execute(sql)
            row = cursor.fetchone()
            
            if row:
                result = f'登录成功！欢迎, {row[1]}！'
                result_type = 'success'
            else:
                result = '登录失败，用户名或密码错误'
                result_type = 'error'
                
        except Exception as e:
            result = f'SQL执行失败: {str(e)}'
            result_type = 'error'
        finally:
            conn.close()
    
    return render_template_string(HTML_TEMPLATE,
                                 title=title,
                                 gradient_start=gradient_start,
                                 gradient_end=gradient_end,
                                 username=username,
                                 password=password,
                                 result=result,
                                 result_type=result_type,
                                 sql=sql_query,
                                 info=info)
