#!/usr/bin/env python3
import http.server
import socketserver
import urllib.parse
import pickle
import base64

FLAG = "Mlai{python_pickle_flag}"

def get_flag():
    global FLAG
    return FLAG

class FlagReader:
    def __init__(self):
        pass
    
    def __reduce__(self):
        return (get_flag, ())

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html().encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            params = urllib.parse.parse_qs(post_data)
            data = params.get('data', [''])[0]
            
            result = ""
            if data:
                result = f"<strong>输入数据 (Base64):</strong> {data}<br><br>"
                try:
                    decoded = base64.b64decode(data)
                    obj = pickle.loads(decoded)
                    result += f"<strong>Python执行结果:</strong><br>反序列化成功\n对象类型: {type(obj).__name__}\n对象值: {obj}"
                    if hasattr(obj, '__call__'):
                        call_result = obj()
                        result += f"\n调用结果: {call_result}"
                except Exception as e:
                    result += f"<strong>Python执行结果:</strong><br>反序列化失败: {str(e)}"
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html(result).encode())
        else:
            super().do_POST()
    
    def get_html(self, result=""):
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Python反序列化漏洞</title>
    <style>
        body {{
            font-family: monospace;
            background: #1a1a2e;
            color: #fff;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: #16213e;
            padding: 30px;
            border-radius: 10px;
            border: 1px solid #0f3460;
        }}
        h1 {{ color: #00ff88; border-bottom: 1px solid #0f3460; padding-bottom: 10px; }}
        textarea {{
            width: 100%;
            height: 80px;
            padding: 10px;
            background: #0d1117;
            border: 1px solid #0f3460;
            border-radius: 5px;
            color: #fff;
            font-family: monospace;
            resize: vertical;
            box-sizing: border-box;
        }}
        button {{
            padding: 10px 20px;
            background: #00ff88;
            border: none;
            border-radius: 5px;
            color: #1a1a2e;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }}
        .result {{
            background: rgba(0, 255, 136, 0.1);
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            white-space: pre-wrap;
        }}
        .hint {{
            background: rgba(255, 255, 0, 0.1);
            padding: 10px;
            border-radius: 5px;
            margin-top: 15px;
            color: #ffc107;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Python反序列化漏洞</h1>
        <form method="POST">
            <label>输入pickle数据（Base64编码）：</label><br><br>
            <textarea name="data" placeholder="例如：gASVowAAAAAAAACMC..."></textarea>
            <button type="submit">提交</button>
        </form>
        <div class="result">{result}</div>
        <div class="hint">
            <strong>提示：</strong>构造恶意的pickle数据执行系统命令读取服务器上的flag文件<br>
            <strong>提示：</strong>pickle反序列化会执行对象的__reduce__方法，可以利用这一点执行任意代码
        </div>
    </div>
</body>
</html>
'''

if __name__ == "__main__":
    PORT = 80
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Python反序列化漏洞服务器运行在端口 {PORT}")
        httpd.serve_forever()
