<!DOCTYPE html>
<html>
<head>
    <title>XSS测试 - 反射型</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        input[type="text"] { width: 100%; padding: 12px; font-size: 16px; border: 2px solid #ddd; border-radius: 6px; box-sizing: border-box; margin: 10px 0; }
        button { padding: 12px 30px; background: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; }
        .output { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 6px; }
        .hint { margin-top: 20px; padding: 15px; background: #fff3cd; border: 1px solid #ffeeba; border-radius: 6px; color: #856404; font-size: 14px; }
    </style>
    <script>
        function showFlag() {
            alert('🎉 Flag获取成功！\n\nMlai{xss_reflected_flag}');
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>🔍 XSS测试 - 反射型</h1>

        <form method="POST">
            <input type="text" name="x" placeholder="输入内容" size="60">
            <button type="submit">提交测试</button>
        </form>

        <div class="output">
            <strong>输出结果：</strong>
            <?php
            $input = '';
            if(isset($_POST['x'])) {
                $input = $_POST['x'];
            } elseif(isset($_GET['data'])) {
                $input = $_GET['data'];
            } elseif(isset($_GET['x'])) {
                $input = $_GET['x'];
            }
            echo $input;
            ?>
        </div>

        </div>
</body>
</html>
