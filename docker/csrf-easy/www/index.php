<!DOCTYPE html>
<html>
<head>
    <title>CSRF测试 - Easy</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        input[type="password"] { width: 100%; padding: 12px; font-size: 16px; border: 2px solid #ddd; border-radius: 6px; box-sizing: border-box; margin: 10px 0; }
        button { padding: 12px 30px; background: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; }
        .result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 6px; }
        .success { color: #28a745; font-weight: bold; }
        .hint { margin-top: 20px; padding: 15px; background: #fff3cd; border: 1px solid #ffeeba; border-radius: 6px; color: #856404; font-size: 14px; }
        .flag-box { margin-top: 20px; padding: 20px; background: #d4edda; border: 2px solid #28a745; border-radius: 10px; text-align: center; font-size: 18px; font-weight: bold; color: #155724; }
        .info { margin-top: 15px; padding: 10px; background: #e7f3ff; border: 1px solid #b6d4fe; border-radius: 6px; color: #0c63e4; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 CSRF测试 - 简单模式</h1>
        
        <div class="info">
            当前用户: <strong>admin</strong> | 密码: <strong>admin123</strong>
        </div>

        <form method="POST">
            <label>修改密码：</label>
            <input type="password" name="password" placeholder="输入新密码">
            <br><br>
            <button type="submit">更新密码</button>
        </form>

        <div class="hint">
            <strong>💡 提示：</strong>
            <p>尝试构造一个CSRF攻击，将密码修改为 "hacked!"</p>
            <p>然后访问 ?get_flag 获取Flag</p>
        </div>

        <?php
        session_start();

        $flag = "Mlai{CSRF-Easy-Success}";

        if (!isset($_SESSION['user'])) {
            $_SESSION['user'] = 'admin';
            $_SESSION['password'] = 'admin123';
        }

        if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['password'])) {
            $_SESSION['password'] = $_POST['password'];
            echo '<div class="result success">✅ 密码已更新为: ' . htmlspecialchars($_POST['password']) . '</div>';
        }

        if (isset($_GET['get_flag']) && $_SESSION['password'] === 'hacked!') {
            echo '<div class="flag-box">🎉 Flag获取成功！<br>' . $flag . '</div>';
        } elseif (isset($_GET['get_flag'])) {
            echo '<div class="result">❌ 密码不正确，请先将密码修改为 "hacked!"</div>';
        }
        ?>
    </div>
</body>
</html>
