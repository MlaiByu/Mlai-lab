<!DOCTYPE html>
<html>
<head>
    <title>PHP反序列化测试</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        textarea { width: 100%; padding: 12px; font-size: 14px; border: 2px solid #ddd; border-radius: 6px; box-sizing: border-box; height: 150px; margin: 10px 0; }
        button { padding: 12px 30px; background: #dc3545; color: white; border: none; border-radius: 6px; cursor: pointer; }
        .result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 6px; }
        .hint { margin-top: 20px; padding: 15px; background: #fff3cd; border: 1px solid #ffeeba; border-radius: 6px; color: #856404; font-size: 14px; }
        .flag-box { margin-top: 20px; padding: 20px; background: #d4edda; border: 2px solid #28a745; border-radius: 10px; text-align: center; font-size: 18px; font-weight: bold; color: #155724; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔓 PHP反序列化测试</h1>
        
        <form method="POST">
            <textarea name="data" placeholder="输入序列化数据"></textarea>
            <br>
            <button type="submit">提交</button>
        </form>

        <div class="hint">
            <strong>💡 提示：</strong>
            <p>服务器会反序列化你提交的数据。</p>
            <p>查看源代码，寻找可以利用的类。</p>
            <p>目标：读取 /var/www/html/flag.txt 文件</p>
        </div>

        <?php
        class FileReader {
            public $filename;
            public function __destruct() {
                if (file_exists($this->filename)) {
                    echo '<div class="flag-box">🎉 Flag获取成功！<br>' . file_get_contents($this->filename) . '</div>';
                }
            }
        }

        if (isset($_POST['data'])) {
            echo '<div class="result"><strong>输出结果：</strong></div>';
            try {
                unserialize($_POST['data']);
            } catch (Exception $e) {
                echo '<div class="result">❌ 反序列化失败: ' . htmlspecialchars($e->getMessage()) . '</div>';
            }
        }
        ?>
    </div>
</body>
</html>
