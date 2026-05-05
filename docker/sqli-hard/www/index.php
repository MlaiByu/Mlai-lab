<!DOCTYPE html>
<html>
<head>
    <title>SQL注入靶场 - 高级</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            width: 350px;
        }
        .login-container h2 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 24px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: bold;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
            box-sizing: border-box;
        }
        .form-group input:focus {
            border-color: #9b59b6;
            outline: none;
        }
        .btn-login {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn-login:hover {
            transform: translateY(-2px);
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
        }
        .result.success {
            background: #d4edda;
            color: #155724;
        }
        .result.error {
            background: #f8d7da;
            color: #721c24;
        }
        .sql-display {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            font-family: monospace;
            font-size: 12px;
            color: #333;
            word-break: break-all;
        }
        .sql-label {
            font-weight: bold;
            color: #9b59b6;
            margin-bottom: 5px;
            display: block;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>用户登录</h2>

        <form method="GET" action="index.php">
            <div class="form-group">
                <label for="username">用户名</label>
                <input type="text" id="username" name="username" placeholder="请输入用户名">
            </div>

            <div class="form-group">
                <label for="password">密码</label>
                <input type="password" id="password" name="password" placeholder="请输入密码">
            </div>

            <button type="submit" class="btn-login">登录</button>
        </form>

        <?php
        $host = 'mysql';
        $user = 'root';
        $pass = 'rootpass';
        $db = 'sqli_db';

        $conn = null;
        $max_attempts = 10;
        $attempt = 0;

        while ($attempt < $max_attempts) {
            $conn = mysqli_connect($host, $user, $pass, $db);
            if ($conn) break;
            $attempt++;
            sleep(2);
        }

        if (!$conn) {
            echo '<div class="result error">数据库连接失败</div>';
            exit;
        }

        if (isset($_GET['username']) && isset($_GET['password'])) {
            $username = $_GET['username'];
            $password = $_GET['password'];

            $filter = ['union', 'select', 'or', 'and', '--', '#', '/*', '*/', 'insert', 'delete', 'update', 'drop'];
            foreach($filter as $word){
                $username = preg_replace('/'.preg_quote($word, '/').'/i', '', $username);
            }

            $sql = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
            $result = mysqli_query($conn, $sql);

            echo '<div class="sql-display">';
            echo '<span class="sql-label">执行的SQL语句：</span>';
            echo htmlspecialchars($sql);
            echo '</div>';

            if (!$result) {
                echo '<div class="result error">SQL执行失败: ' . mysqli_error($conn) . '</div>';
            } elseif ($row = mysqli_fetch_array($result)) {
                echo '<div class="result success">登录成功！欢迎, ' . htmlspecialchars($row['username']) . '！</div>';
            } else {
                echo '<div class="result error">登录失败，用户名或密码错误</div>';
            }
        }
        ?>
    </div>
</body>
</html>