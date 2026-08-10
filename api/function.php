<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Accept');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

$host = '127.0.0.1';
$dbname = 'kbd_hr_boarding';
$dbuser = 'root';
$dbpass = '';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $dbuser, $dbpass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
    ]);

    $method = $_SERVER['REQUEST_METHOD'];
    $input = json_decode(file_get_contents('php://input'), true) ?: [];
    $id = isset($input['id']) ? (int)$input['id'] : (isset($_GET['id']) ? (int)$_GET['id'] : 0);

    function respond(array $data)
    {
        echo json_encode($data, JSON_UNESCAPED_UNICODE);
        exit;
    }

    function fail(string $message, int $code = 400)
    {
        http_response_code($code);
        respond(['success' => false, 'message' => $message]);
    }

    switch ($method) {
        case 'GET':
            if ($id > 0) {
                $stmt = $pdo->prepare('SELECT * FROM `functions` WHERE id = :id');
                $stmt->execute([':id' => $id]);
                $func = $stmt->fetch();
                respond(['success' => true, 'function' => $func ?: null]);
            }

            $stmt = $pdo->query('SELECT * FROM `functions` ORDER BY id ASC');
            $functions = $stmt->fetchAll();
            respond(['success' => true, 'functions' => $functions]);
            break;

        case 'POST':
            $stmt = $pdo->prepare('INSERT INTO `functions` (`function`) VALUES (:function)');
            $stmt->execute([':function' => $input['function'] ?? '']);
            $newId = (int)$pdo->lastInsertId();

            $stmt = $pdo->prepare('SELECT * FROM `functions` WHERE id = :id');
            $stmt->execute([':id' => $newId]);
            $func = $stmt->fetch();

            respond(['success' => true, 'function' => $func, 'id' => $newId]);
            break;

        case 'PUT':
            if ($id <= 0) {
                http_response_code(400);
                echo json_encode(['success' => false, 'message' => 'Ungültige ID.']);
                exit;
            }

            $stmt = $pdo->prepare('UPDATE `functions` SET `function` = :function WHERE id = :id');
            $stmt->execute([':id' => $id, ':function' => $input['function'] ?? '']);
            respond(['success' => true, 'id' => $id]);
            break;

        case 'DELETE':
            if ($id <= 0) {
                http_response_code(400);
                echo json_encode(['success' => false, 'message' => 'Ungültige ID.']);
                exit;
            }

            $stmt = $pdo->prepare('DELETE FROM `functions` WHERE id = :id');
            $stmt->execute([':id' => $id]);
            respond(['success' => true]);
            break;

        default:
            fail('Methode nicht erlaubt.', 405);
    }
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Datenbankfehler: ' . $e->getMessage()]);
}