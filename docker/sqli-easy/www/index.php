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

if (!$conn) die("数据库连接失败");

$id = $_GET['id'];
$sql = "SELECT * FROM users WHERE id = $id";
$result = mysqli_query($conn, $sql);

if($row = mysqli_fetch_array($result)){
    echo "ID：".$row['id']."<br>";
    echo "用户名：".$row['username']."<br>";
    echo "密码：".$row['password']."<br>";
}else{
    echo "无数据";
}
?>