<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>存储型 XSS</title>
    <style>
        body {
            font-family: monospace;
            background: #1a1a2e;
            color: #fff;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: #16213e;
            padding: 30px;
            border-radius: 10px;
            border: 1px solid #0f3460;
        }
        h1 {
            color: #00ff88;
            border-bottom: 1px solid #0f3460;
            padding-bottom: 10px;
        }
        textarea {
            width: 100%;
            height: 100px;
            padding: 10px;
            background: #0d1117;
            border: 1px solid #0f3460;
            border-radius: 5px;
            color: #fff;
            font-family: monospace;
            resize: vertical;
        }
        button {
            padding: 10px 20px;
            background: #00ff88;
            border: none;
            border-radius: 5px;
            color: #1a1a2e;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }
        .messages {
            background: rgba(0, 255, 136, 0.1);
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .hint {
            background: rgba(255, 255, 0, 0.1);
            padding: 10px;
            border-radius: 5px;
            margin-top: 15px;
            color: #ffc107;
        }
        .flag-box {
            background: rgba(0, 255, 136, 0.05);
            border: 1px dashed #00ff88;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-family: monospace;
            font-size: 12px;
        }
        code {
            background: #0d1117;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>存储型 XSS 实验</h1>
        <form method="POST">
            留言内容：<textarea name="msg" placeholder="尝试注入 JavaScript 代码"></textarea>
            <button type="submit">提交留言</button>
        </form>
        <hr>
        <h3>历史留言</h3>
        <div class="messages">
            <?php
            if(isset($_POST['msg'])){
                file_put_contents("data.txt", $_POST['msg']."<br>", FILE_APPEND);
            }
            if(file_exists("data.txt")){
                echo file_get_contents("data.txt");
            } else {
                echo "暂无留言...";
            }
            ?>
        </div>

        <div class="hint">
            <strong>提示：</strong>浏览器会阻止直接的 &lt;script&gt; 标签执行<br>
            <strong>正确方法：</strong>使用事件处理属性注入<br>
            <code>&lt;img src=x onerror=alert(flag)&gt;</code>
        </div>
        
        <div class="flag-box">
            <strong>提示：</strong>页面中有一个全局变量 flag，尝试用 XSS 获取它！
        </div>
    </div>

    <script>
        window.flag = "Mlai{xss_stored_flag}";
        console.log("Flag:", window.flag);
        document.getElementById('flag-hint').innerHTML = window.flag;
    </script>
</body>
</html>
