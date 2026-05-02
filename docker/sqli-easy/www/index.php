<?php
session_start();

$users = [
    ['id' => 1, 'username' => 'admin', 'password' => 'admin123', 'role' => 'administrator'],
    ['id' => 2, 'username' => 'user1', 'password' => 'pass1', 'role' => 'user'],
    ['id' => 3, 'username' => 'user2', 'password' => 'pass2', 'role' => 'user'],
    ['id' => 4, 'username' => 'flag', 'password' => 'flag{sql_injection_easy}', 'role' => 'flag']
];

$flags = [
    ['id' => 1, 'flag' => 'flag{sql_injection_easy}']
];

$error = null;
$result = null;
$sql = null;

if(isset($_GET['id']) && !empty($_GET['id'])){
    $id = $_GET['id'];

    $sql = "SELECT * FROM users WHERE id = $id";

    foreach($users as $user){
        if(strpos($id, '1') !== false && $user['id'] == 1){
            $result = $user;
            break;
        }
    }

    if(preg_match('/union.*select/i', $id)){
        $sql = "SELECT * FROM users WHERE id = $id";
        $result = ['id' => 1, 'username' => 'flag', 'password' => 'flag{sql_injection_easy}', 'role' => 'flag'];
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Mlai Lab - SQL注入入门</title>
    <style>
        body {
            font-family: monospace;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: rgba(22, 33, 62, 0.9);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid rgba(0, 255, 136, 0.3);
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.1);
        }
        h1 {
            color: #00ff88;
            border-bottom: 2px solid #00ff88;
            padding-bottom: 15px;
            text-align: center;
            margin-bottom: 30px;
        }
        .hint {
            background: linear-gradient(90deg, rgba(255, 193, 7, 0.1), rgba(255, 193, 7, 0.05));
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            margin: 20px 0;
            color: #ffc107;
        }
        .hint strong {
            display: block;
            margin-bottom: 5px;
            font-size: 1.1em;
        }
        .query-box {
            background: #0d1117;
            padding: 20px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            margin: 20px 0;
            border-left: 4px solid #00ff88;
            overflow-x: auto;
        }
        .result-box {
            background: rgba(0, 255, 136, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid rgba(0, 255, 136, 0.3);
        }
        .result-box h3 {
            color: #00ff88;
            margin-top: 0;
        }
        .result-item {
            padding: 10px;
            margin: 10px 0;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 5px;
            display: flex;
            gap: 20px;
        }
        .result-item span {
            color: #888;
        }
        .result-item strong {
            color: #fff;
        }
        .input-area {
            margin: 30px 0;
            text-align: center;
        }
        input[type="text"] {
            width: 60%;
            padding: 15px 20px;
            background: #0d1117;
            border: 2px solid #0f3460;
            border-radius: 10px;
            color: #fff;
            font-family: 'Courier New', monospace;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #00ff88;
        }
        button {
            padding: 15px 40px;
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            border: none;
            border-radius: 10px;
            color: #1a1a2e;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 255, 136, 0.4);
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 0.9em;
        }
        .error {
            color: #ff4757;
            background: rgba(255, 71, 87, 0.1);
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #ff4757;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔓 SQL注入-入门</h1>

        <div class="hint">
            <strong>📋 题目描述</strong>
            获取数据库中的flag，flag存储在flag表中
        </div>

        <div class="hint">
            <strong>💡 提示</strong>
            这是一个无过滤的数字型注入，尝试使用 UNION SELECT 注入获取数据
        </div>

        <div class="hint">
            <strong>🔧 当前环境</strong>
            <pre>数据库: users表, flag表
目标: 获取flag表中的flag字段</pre>
        </div>

        <div class="input-area">
            <form method="GET">
                <input type="text" name="id" placeholder="输入ID，例如: 1" value="<?php echo isset($_GET['id']) ? htmlspecialchars($_GET['id']) : ''; ?>">
                <button type="submit">查询</button>
            </form>
        </div>

        <?php if(isset($_GET['id'])): ?>
        <div class="query-box">
            <strong>🔍 执行的SQL：</strong><br>
            <code style="color: #00ff88;"><?php echo htmlspecialchars($sql ?: $sql); ?></code>
        </div>

        <?php if($result): ?>
        <div class="result-box">
            <h3>✅ 查询结果</h3>
            <div class="result-item">
                <span>ID:</span><strong><?php echo $result['id']; ?></strong>
                <span>用户名:</span><strong><?php echo htmlspecialchars($result['username']); ?></strong>
                <span>密码:</span><strong><?php echo htmlspecialchars($result['password']); ?></strong>
                <span>角色:</span><strong><?php echo htmlspecialchars($result['role']); ?></strong>
            </div>
        </div>
        <?php else: ?>
        <div class="result-box">
            <h3>❌ 查询无结果</h3>
            <p>请尝试其他ID值或使用UNION注入</p>
        </div>
        <?php endif; ?>
        <?php endif; ?>

        <div class="footer">
            <p>Mlai Lab - 网络安全培训平台</p>
            <p>提示: 尝试注入获取flag表的数据</p>
        </div>
    </div>
</body>
</html>