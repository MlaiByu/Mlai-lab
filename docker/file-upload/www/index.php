<?php
$flag = "Mlai{file_upload_flag}";

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['file'])) {
    $uploadDir = 'uploads/';
    if (!file_exists($uploadDir)) {
        mkdir($uploadDir, 0777, true);
    }

    $fileName = $_FILES['file']['name'];
    $filePath = $uploadDir . $fileName;

    if (move_uploaded_file($_FILES['file']['tmp_name'], $filePath)) {
        echo "文件上传成功: " . $fileName;
        echo "\nFlag: " . $flag;
    } else {
        echo "文件上传失败";
    }
}
?>