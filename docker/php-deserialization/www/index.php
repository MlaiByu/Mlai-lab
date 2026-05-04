<?php
class FileReader {
    public $filename;
    public function __destruct() {
        if (file_exists($this->filename)) {
            echo file_get_contents($this->filename);
        }
    }
}

if (isset($_POST['data'])) {
    unserialize($_POST['data']);
}
?>