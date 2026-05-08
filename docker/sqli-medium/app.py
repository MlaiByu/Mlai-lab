from flask import Flask, request, render_template_string
import pymysql
import time

app = Flask(__name__)

def get_db_connection():
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            conn = pymysql.connect(
                host='mysql',
                user='root',
                password='rootpass',
                database='sqli_db',
                charset='utf8mb4'
            )
            return conn
        except:
            time.sleep(2)
    return None

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>SQL注入靶场 - 中级</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #f39c12 0%, #e74c3c 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            width: 350px;
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
            box-sizing: border-box;
        }
        .form-group input:focus {
            border-color: #f39c12;
            outline: none;
        }
        .btn-login {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #f39c12 0%, #e74c3c 100%);
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
            color: #f39c12;
            margin-bottom: 5px;
            display: block;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>用户登录</h2>

        <form method="GET" action="/">
            <div class="form-group">
                <label for="username">用户名</label>
                <input type="text" id="username" name="username" placeholder="请输入用户名">
            </div>

            <div class="form-group">
                <label for="password">密码</label>
                <input type="password" id="password" name="password" placeholder="请输入密码">
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
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    result = None
    result_type = None
    sql_query = None
    
    username = request.args.get('username', '')
    password = request.args.get('password', '')
    
    if username and password:
        conn = get_db_connection()
        if not conn:
            return render_template_string(HTML_TEMPLATE, 
                                         result='数据库连接失败', 
                                         result_type='error')
        
        try:
            cursor = conn.cursor()
            
            username = username.replace('--', '').replace('#', '').replace('/*', '')
            
            sql = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
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
                                 result=result, 
                                 result_type=result_type,
                                 sql=sql_query)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
