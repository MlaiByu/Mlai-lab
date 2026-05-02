<?php
$db_host = "mysql";
$db_user = "root";
$db_pwd  = "123456";
$db_name = "sqli_db";

$conn = mysqli_connect($db_host,$db_user,$db_pwd,$db_name);
if(!$conn){
    die("数据库连接失败: " . mysqli_connect_error());
}

$id = isset($_GET['id']) ? $_GET['id'] : '';
$id = str_replace('--', '', $id);
$id = str_replace('#', '', $id);
$id = str_replace('/*', '', $id);

$sql = "select * from users where id = '$id'";
$result = mysqli_query($conn,$sql);

$error = null;
if($result === false){
    $error = mysqli_error($conn);
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Mlai Lab - SQL注入中级</title>
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
            color: #ff6b6b;
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
        .warning {
            background: rgba(255, 107, 107, 0.1);
            padding: 10px;
            border-radius: 5px;
            margin: 15px 0;
            color: #ff6b6b;
        }
        .query {
            background: #0d1117;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            margin: 15px 0;
            border-left: 3px solid #ff6b6b;
        }
        .result {
            background: rgba(255, 107, 107, 0.1);
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
            background: #ff6b6b;
            border: none;
            border-radius: 5px;
            color: #1a1a2e;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover {
            background: #ee5a5a;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SQL注入-中级</h1>
        
        <div class="hint">
            <strong>题目描述：</strong>获取数据库中的flag，flag存储在flag表中
        </div>
        
        <div class="hint">
            <strong>提示：</strong>这是一个字符型注入，尝试闭合单引号后使用 UNION SELECT
        </div>
        
        <div class="warning">
            <strong>警告：</strong>注释符 -- 、# 和 /* 已被过滤，尝试使用其他方式绕过
        </div>

        <div class="input-area">
            <form method="GET">
                <input type="text" name="id" placeholder="输入用户ID" value="<?php echo isset($_GET['id']) ? htmlspecialchars($_GET['id']) : ''; ?>">
                <button type="submit">查询</button>
            </form>
        </div>

        <?php if(isset($id)): ?>
        <div class="query">
            <strong>执行的SQL：</strong><br>
            <?php echo htmlspecialchars($sql); ?>
        </div>

        <div class="result">
            <strong>查询结果：</strong><br>
            <?php
            if(isset($error)){
                echo "<span style='color: #ff4757;'>SQL执行错误：".$error."</span>";
            }elseif($row = mysqli_fetch_assoc($result)){
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
