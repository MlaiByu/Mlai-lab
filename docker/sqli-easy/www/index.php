<?php
session_start();

$host = 'mysql';
$user = 'root';
$pass = 'rootpass';
$db = 'sqli_db';

$error = null;
$result = null;
$sql = null;
$flag_submitted = false;
$flag_correct = false;
$submit_message = '';

$max_attempts = 10;
$attempt = 0;
$conn = null;

while ($attempt < $max_attempts) {
    $conn = @new mysqli($host, $user, $pass, $db);
    if (!$conn->connect_error) {
        break;
    }
    $attempt++;
    sleep(2);
}

if($conn->connect_error){
    $error = "数据库连接失败: " . $conn->connect_error;
}

if(isset($_GET['id']) && !empty($_GET['id']) && !$error){
    $id = $_GET['id'];
    $sql = "SELECT * FROM users WHERE id = $id";
    $res = $conn->query($sql);

    if($res && $res->num_rows > 0){
        $result = $res->fetch_assoc();
    }
}

if(isset($_POST['submit_flag'])){
    $submitted_flag = trim($_POST['flag']);
    if($conn && !$conn->connect_error){
        $res = $conn->query("SELECT flag FROM flag WHERE id = 1");
        if($res && $row = $res->fetch_assoc()){
            if($submitted_flag === $row['flag']){
                $flag_correct = true;
                $submit_message = "🎉 恭喜！Flag提交正确！";
            } else {
                $submit_message = "❌ Flag提交错误，请重试！";
            }
        }
    }
    $flag_submitted = true;
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CTFShow - SQL注入入门</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
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
        .header .subtitle {
            color: #888;
            font-size: 14px;
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
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .card-title::before {
            content: '📋';
        }
        .card-body {
            color: #ccc;
            line-height: 1.6;
        }
        .card-body pre {
            background: #0d1117;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 10px 0;
            font-size: 14px;
            border-left: 3px solid #00ff88;
        }
        .input-group {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .input-group input {
            flex: 1;
            padding: 12px 15px;
            background: #0d1117;
            border: 2px solid #0f3460;
            border-radius: 8px;
            color: #fff;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .input-group input:focus {
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
            transition: transform 0.2s, box-shadow 0.2s;
            font-size: 14px;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 136, 0.4);
        }
        .btn:active {
            transform: translateY(0);
        }
        .sql-display {
            background: #0d1117;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            color: #00ff88;
            border-left: 3px solid #00ff88;
            word-break: break-all;
        }
        .result-box {
            margin-top: 15px;
            padding: 15px;
            border-radius: 8px;
        }
        .result-success {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.3);
        }
        .result-error {
            background: rgba(255, 71, 87, 0.1);
            border: 1px solid rgba(255, 71, 87, 0.3);
        }
        .result-item {
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .result-item:last-child {
            border-bottom: none;
        }
        .result-item span {
            color: #888;
            margin-right: 10px;
        }
        .result-item strong {
            color: #00ff88;
        }
        .flag-section {
            background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(255, 193, 7, 0.05));
            border: 1px solid rgba(255, 193, 7, 0.3);
        }
        .flag-section .card-title::before {
            content: '🎯';
        }
        .flag-result {
            margin-top: 15px;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
        }
        .flag-correct {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
            border: 1px solid rgba(0, 255, 136, 0.5);
        }
        .flag-wrong {
            background: rgba(255, 71, 87, 0.2);
            color: #ff4757;
            border: 1px solid rgba(255, 71, 87, 0.5);
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
        .timer {
            background: rgba(0, 191, 255, 0.1);
            border: 1px solid rgba(0, 191, 255, 0.3);
            padding: 10px 15px;
            border-radius: 8px;
            text-align: center;
            font-family: 'Courier New', monospace;
            font-size: 18px;
            color: #00bfff;
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
            <h1>🔓 SQL注入-入门</h1>
            <div class="subtitle">CTFShow 风格漏洞练习环境</div>
        </div>

        <div class="card">
            <div class="card-title">题目描述</div>
            <div class="card-body">
                <p>获取数据库中的 <strong style="color: #00ff88;">flag</strong>，flag存储在 <strong style="color: #00ff88;">flag</strong> 表中。</p>
                <div class="hint">
                    💡 提示：这是一个无过滤的数字型注入，尝试使用 UNION SELECT 注入获取数据
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-title">当前环境</div>
            <div class="card-body">
                <pre>数据库: sqli_db
表: users, flag
目标: 获取flag表中的flag字段</pre>
            </div>
        </div>

        <div class="card">
            <div class="card-title">SQL查询</div>
            <div class="card-body">
                <form method="GET" class="input-group">
                    <input type="text" name="id" placeholder="输入ID，例如: 1" value="<?php echo isset($_GET['id']) ? htmlspecialchars($_GET['id']) : ''; ?>">
                    <button type="submit" class="btn">查询</button>
                </form>
                
                <?php if(isset($_GET['id'])): ?>
                <div class="sql-display">
                    <strong>执行的SQL：</strong><br>
                    SELECT * FROM users WHERE id = <?php echo htmlspecialchars($_GET['id']); ?>
                </div>

                <div class="result-box <?php echo $result ? 'result-success' : 'result-error'; ?>">
                    <?php if($result): ?>
                        <div class="result-item">
                            <span>ID:</span><strong><?php echo $result['id']; ?></strong>
                        </div>
                        <div class="result-item">
                            <span>用户名:</span><strong><?php echo htmlspecialchars($result['username']); ?></strong>
                        </div>
                        <div class="result-item">
                            <span>密码:</span><strong><?php echo htmlspecialchars($result['password']); ?></strong>
                        </div>
                    <?php else: ?>
                        <p style="color: #ff4757;">查询无结果，请尝试其他ID值或使用UNION注入</p>
                    <?php endif; ?>
                </div>
                <?php endif; ?>
            </div>
        </div>

        <div class="card flag-section">
            <div class="card-title">提交Flag</div>
            <div class="card-body">
                <form method="POST" class="input-group">
                    <input type="text" name="flag" placeholder="输入获取到的flag" value="<?php echo isset($_POST['flag']) ? htmlspecialchars($_POST['flag']) : ''; ?>">
                    <button type="submit" name="submit_flag" class="btn">提交</button>
                </form>
                
                <?php if($flag_submitted): ?>
                <div class="flag-result <?php echo $flag_correct ? 'flag-correct' : 'flag-wrong'; ?>">
                    <?php echo $submit_message; ?>
                </div>
                <?php endif; ?>
            </div>
        </div>

        <div class="footer">
            <p>Mlai Lab - 网络安全培训平台</p>
            <p>端口: <?php echo $_SERVER['SERVER_PORT']; ?> | 环境ID: sqli-easy</p>
        </div>
    </div>
</body>
</html>