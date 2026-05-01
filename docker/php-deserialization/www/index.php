<?php
class User {
    public $username;
    public function __construct() {}
    public function __destruct() {
        return "欢迎, " . $this->username . "<br>";
    }
}

class FileReader {
    public $filename;
    public $flag = "Mlai{php_unserialize_flag}";
    public function __destruct() {
        return "<br><strong>文件内容:</strong><br><span style='color: #00ff88; font-size: 16px;'>" . $this->flag . "</span>";
    }
}

$deserialize_result = "";
$input_data = "";

if (isset($_POST['data'])) {
    $input_data = $_POST['data'];
    $obj = unserialize($input_data);
    if (method_exists($obj, '__destruct')) {
        $deserialize_result = $obj->__destruct();
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>PHP反序列化漏洞</title>
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
        h1 { color: #00ff88; border-bottom: 1px solid #0f3460; padding-bottom: 10px; }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            background: #0d1117;
            border: 1px solid #0f3460;
            border-radius: 5px;
            color: #fff;
            font-family: monospace;
            box-sizing: border-box;
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
        .result {
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
    </style>
</head>
<body>
    <div class="container">
        <h1>PHP反序列化漏洞</h1>
        <form method="POST">
            <label>输入序列化数据：</label><br><br>
            <input type="text" name="data" placeholder="例如：O:8:\"User\":1:{s:8:\"username\";s:5:\"admin\";}">
            <button type="submit">提交</button>
        </form>
        <div class="result">
            <?php if ($input_data): ?>
            <strong>输入数据:</strong><br>
            <code style="display: block; margin: 5px 0; padding: 10px; background: #0d1117; border-radius: 4px; word-break: break-all;"><?php echo htmlspecialchars($input_data); ?></code><br>
            <strong>反序列化结果:</strong><br>
            <?php echo $deserialize_result; ?>
            <?php else: ?>
            <strong>提示：</strong>在此输入序列化数据进行反序列化测试
            <?php endif; ?>
        </div>
        <div class="hint">
            <strong>提示：</strong>构造恶意的序列化数据读取服务器上的flag文件<br>
            <strong>提示：</strong>查看页面中的类定义，利用FileReader类读取敏感文件
        </div>
    </div>
</body>
</html>
