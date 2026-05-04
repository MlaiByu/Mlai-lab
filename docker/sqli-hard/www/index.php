<?php
$db_host = "mysql";
$db_user = "root";
$db_pwd  = "rootpass";
$db_name = "sqli_db";

try {
    $conn = new PDO("mysql:host=$db_host;dbname=$db_name", $db_user, $db_pwd);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch(PDOException $e) {
    die("数据库连接失败: " . $e->getMessage());
}

$id = isset($_GET['id']) ? $_GET['id'] : '';

$filter = ['union', 'select', 'or', 'and', '--', '#', '/*', '*/', 'insert', 'delete', 'update', 'drop'];
foreach($filter as $word){
    $id = preg_replace('/'.preg_quote($word, '/').'/i', '', $id);
}

$sql = "select * from users where id = $id";
$result = null;
$error = null;

try {
    $result = $conn->query($sql);
} catch(PDOException $e) {
    $error = $e->getMessage();
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Mlai Lab - SQL注入高级</title>
    <style>
        body {
            font-family: monospace;
            background: #1a1a2e;
            color: #fff;
            padding: 20px;
        }
        .container {
            max-width: 800px;
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
        .hint {
            background: rgba(255, 255, 0, 0.1);
            padding: 10px;
            border-radius: 5px;
            margin: 15px 0;
            color: #ffc107;
        }
        .query {
            background: #0d1117;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            margin: 15px 0;
            border-left: 3px solid #00ff88;
        }
        .result {
            background: rgba(0, 255, 136, 0.1);
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .input-area {
            margin-top: 20px;
        }
        input[type="text"] {
            width: 70%;
            padding: 10px;
            background: #0d1117;
            border: 1px solid #0f3460;
            border-radius: 5px;
            color: #fff;
            font-family: monospace;
        }
        button {
            padding: 10px 20px;
            background: #00ff88;
            border: none;
            border-radius: 5px;
            color: #1a1a2e;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover {
            background: #00cc6a;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SQL注入-高级</h1>

        <div class="hint">
            <strong>题目描述：</strong>获取数据库中的flag，flag存储在flag表中
        </div>

        <div class="hint">
            <strong>提示：</strong>过滤了很多关键词，尝试使用大小写混淆或其他绕过方式
        </div>

        <div class="input-area">
            <form method="GET">
                <input type="text" name="id" placeholder="输入ID" value="<?php echo isset($_GET['id']) ? htmlspecialchars($_GET['id']) : ''; ?>">
                <button type="submit">查询</button>
            </form>
        </div>

        <?php if(!empty($id)): ?>
        <div class="query">
            <strong>执行的SQL：</strong><br>
            <?php echo htmlspecialchars($sql); ?>
        </div>

        <div class="result">
            <strong>查询结果：</strong><br>
            <?php
            if(isset($error)){
                echo "<span style='color: #ff4757;'>SQL执行错误：".$error."</span>";
            }elseif($row = $result->fetch(PDO::FETCH_ASSOC)){
                echo "用户名：".$row['username']."<br>";
                echo "密码：".$row['password'];
            }else{
                echo "查询无结果";
            }
            ?>
        </div>
        <?php endif; ?>
    </div>
</body>
</html>