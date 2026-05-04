<?php
$dataFile = 'data.txt';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['message'])) {
    $message = $_POST['message'];
    $time = date('Y-m-d H:i:s');
    $entry = "$time - $message\n";
    file_put_contents($dataFile, $entry, FILE_APPEND);
}

if (file_exists($dataFile)) {
    echo file_get_contents($dataFile);
}
?>