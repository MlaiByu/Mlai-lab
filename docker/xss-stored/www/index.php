<!DOCTYPE html>
<html>
<head>
    <title>XSS测试 - 存储型</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        textarea { width: 100%; padding: 12px; font-size: 14px; border: 2px solid #ddd; border-radius: 6px; box-sizing: border-box; height: 80px; margin: 10px 0; }
        button { padding: 12px 30px; background: #28a745; color: white; border: none; border-radius: 6px; cursor: pointer; }
        .messages { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 6px; }
        .hint { margin-top: 20px; padding: 15px; background: #fff3cd; border: 1px solid #ffeeba; border-radius: 6px; color: #856404; font-size: 14px; }
    </style>
    <script>
        function showFlag() {
            alert('🎉 Flag获取成功！\n\nMlai{XSS-Stored-Success}');
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>📝 XSS测试 - 存储型</h1>
        
        <form method="POST">
            <textarea name="msg" placeholder="输入留言"></textarea>
            <button type="submit">提交留言</button>
        </form>
        
        <div class="messages">
            <strong>留言列表：</strong>
            <div>
                <?php
                $file = '/tmp/messages.txt';
                if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['msg'])) {
                    file_put_contents($file, $_POST['msg'] . '<br>', FILE_APPEND);
                }
                if (file_exists($file)) {
                    echo file_get_contents($file);
                } else {
                    echo '<p style="color: #999;">暂无留言</p>';
                }
                ?>
            </div>
        </div>

        </div>
</body>
</html>
