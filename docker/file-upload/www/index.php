<!DOCTYPE html>
<html>
<head>
    <title>文件上传漏洞</title>
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
        form { margin-top: 20px; }
        input[type="file"] {
            margin: 10px 0;
            padding: 10px;
            background: #0d1117;
            border: 1px solid #0f3460;
            border-radius: 5px;
            color: #fff;
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
        .success { color: #00ff88; }
        .error { color: #ff4757; }
    </style>
</head>
<body>
    <div class="container">
        <h1>文件上传漏洞</h1>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" accept=".jpg,.png,.gif">
            <button type="submit">上传文件</button>
        </form>
        
        <div class="result">
            <?php
            $flag = "Mlai{file_upload_flag}";
            
            if ($_SERVER['REQUEST_METHOD'] === 'POST') {
                if (isset($_FILES['file'])) {
                    $uploadDir = 'uploads/';
                    $fileName = $_FILES['file']['name'];
                    $filePath = $uploadDir . $fileName;
                    
                    if (!file_exists($uploadDir)) {
                        mkdir($uploadDir, 0777, true);
                    }
                    
                    $allowedExts = array('jpg', 'jpeg', 'png', 'gif');
                    $fileExt = strtolower(pathinfo($fileName, PATHINFO_EXTENSION));
                    
                    if (in_array($fileExt, $allowedExts)) {
                        if (move_uploaded_file($_FILES['file']['tmp_name'], $filePath)) {
                            echo "<span class='success'>文件上传成功: " . htmlspecialchars($fileName) . "</span>";
                            echo "<br>访问路径: <a href='" . $filePath . "' target='_blank'>" . $filePath . "</a>";
                            
                            if (strpos($fileName, 'php') !== false || strpos($fileName, '.php') !== false) {
                                echo "<br><br><strong style='color: #00ff88; font-size: 16px;'>Flag: " . $flag . "</strong>";
                            }
                        } else {
                            echo "<span class='error'>文件上传失败</span>";
                        }
                    } else {
                        echo "<span class='error'>不允许的文件类型</span>";
                    }
                } else {
                    echo "<span class='error'>请选择文件</span>";
                }
            } else {
                echo "<strong>提示：</strong>上传文件到服务器";
            }
            ?>
        </div>
        
        <div class="hint">
            <strong>提示：</strong>尝试上传PHP文件获取服务器上的flag<br>
            <strong>提示：</strong>可以尝试修改文件名绕过扩展名检测
        </div>
    </div>
</body>
</html>