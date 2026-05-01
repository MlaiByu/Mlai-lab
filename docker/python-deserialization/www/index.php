<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Python反序列化漏洞</title>
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
        textarea {
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
            white-space: pre-wrap;
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
        <h1>Python反序列化漏洞</h1>
        <form method="POST">
            <label>输入pickle数据（Base64编码）：</label><br><br>
            <textarea name="data" placeholder="例如：gASVowAAAAAAAACMC..."></textarea>
            <button type="submit">提交</button>
        </form>
        <div class="result">
            <?php
            file_put_contents("/var/www/html/flag.txt", "Mlai{python_pickle_flag}");
            
            if (isset($_POST['data'])) {
                $data = $_POST['data'];
                echo "<strong>输入数据 (Base64):</strong> " . htmlspecialchars($data) . "<br><br>";
                
                $temp_file = tempnam(sys_get_temp_dir(), "pickle_");
                file_put_contents($temp_file, base64_decode($data));
                
                $python_script = <<<'PYTHON'
import pickle
import sys

with open(sys.argv[1], 'rb') as f:
    data = f.read()

try:
    obj = pickle.loads(data)
    print("反序列化成功")
    print("对象类型:", type(obj).__name__)
    print("对象值:", obj)
except Exception as e:
    print("反序列化失败:", str(e))
PYTHON;
                
                $python_file = tempnam(sys_get_temp_dir(), "script_") . ".py";
                file_put_contents($python_file, $python_script);
                
                $output = shell_exec("python3 " . escapeshellarg($python_file) . " " . escapeshellarg($temp_file));
                
                echo "<strong>Python执行结果:</strong><br>";
                echo nl2br(htmlspecialchars($output));
                
                unlink($temp_file);
                unlink($python_file);
            }
            ?>
        </div>
        <div class="hint">
            <strong>提示：</strong>构造恶意的pickle数据执行系统命令读取flag<br>
            <strong>Flag:</strong> Mlai{python_pickle_flag}
        </div>
    </div>
</body>
</html>
