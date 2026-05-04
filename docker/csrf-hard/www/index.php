<?php
session_start();

$flag = "Mlai{CSRF-Hard-Success}";

if (!isset($_SESSION['user'])) {
    $_SESSION['user'] = 'admin';
    $_SESSION['password'] = 'admin123';
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['password'])) {
    if (!isset($_SERVER['HTTP_REFERER']) || strpos($_SERVER['HTTP_REFERER'], $_SERVER['HTTP_HOST']) === false) {
        echo "Referer验证失败";
    } else {
        $_SESSION['password'] = $_POST['password'];
        echo "密码已更新为: " . $_POST['password'];
    }
}

if (isset($_GET['get_flag']) && $_SESSION['password'] === 'hacked!') {
    echo "Flag: " . $flag;
}
?>