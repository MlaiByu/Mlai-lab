<!DOCTYPE html>
<html>
<head>
    <title>文件上传测试</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        input[type="file"] { margin: 10px 0; }
        button { padding: 12px 30px; background: #28a745; color: white; border: none; border-radius: 6px; cursor: pointer; }
        .result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 6px; }
        .success { color: #28a745; font-weight: bold; }
        .error { color: #dc3545; }
        .hint { margin-top: 20px; padding: 15px; background: #fff3cd; border: 1px solid #ffeeba; border-radius: 6px; color: #856404; font-size: 14px; }
        .flag-box { margin-top: 20px; padding: 20px; background: #d4edda; border: 2px solid #28a745; border-radius: 10px; text-align: center; font-size: 18px; font-weight: bold; color: #155724; }
        .uploaded-files { margin-top: 20px; }
        .file-link { display: block; margin: 5px 0; padding: 8px; background: #e7f3ff; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📤 文件上传测试</h1>
        
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" accept=".jpg,.png,.gif">
            <br><br>
            <button type="submit">上传文件</button>
        </form>

        <div class="hint">
            <strong>💡 提示：</strong>
            <p>服务器只允许上传图片文件（jpg, png, gif）。</p>
            <p>尝试上传一个PHP文件来获取服务器上的flag。</p>
            <p>提示：尝试使用文件扩展名绕过技术。</p>
        </div>

        <?php
        $flag = "Mlai{file_upload_flag}";

        if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['file'])) {
            $uploadDir = 'uploads/';
            if (!file_exists($uploadDir)) {
                mkdir($uploadDir, 0777, true);
            }

            $fileName = $_FILES['file']['name'];
            $filePath = $uploadDir . $fileName;
            $fileExt = strtolower(pathinfo($fileName, PATHINFO_EXTENSION));

            $allowedExts = array('jpg', 'jpeg', 'png', 'gif');
            
            if (!in_array($fileExt, $allowedExts)) {
                echo '<div class="result error">❌ 错误：只允许上传图片文件（jpg, png, gif）</div>';
            } else {
                if (move_uploaded_file($_FILES['file']['tmp_name'], $filePath)) {
                    echo '<div class="result success">✅ 文件上传成功: ' . htmlspecialchars($fileName) . '</div>';
                    echo '<div class="uploaded-files">';
                    echo '<strong>已上传的文件：</strong><br>';
                    $files = glob($uploadDir . '*');
                    foreach ($files as $file) {
                        $basename = basename($file);
                        echo "<a href='uploads/$basename' class='file-link' target='_blank'>📄 $basename</a>";
                    }
                    echo '</div>';
                } else {
                    echo '<div class="result error">❌ 文件上传失败</div>';
                }
            }
        }
        ?>
    </div>
</body>
</html>
