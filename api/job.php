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

    try {
        switch ($method) {
            case 'GET':
                if ($id > 0) {
                    $stmt = $pdo->prepare('SELECT * FROM jobs WHERE id = :id');
                    $stmt->execute([':id' => $id]);
                    $job = $stmt->fetch();
                    echo json_encode(['success' => true, 'job' => $job ?: null]);
                    exit;
                }

                $stmt = $pdo->query('SELECT * FROM jobs ORDER BY id ASC');
                $jobs = $stmt->fetchAll();
                echo json_encode(['success' => true, 'jobs' => $jobs]);
                exit;
            case 'POST':
                $stmt = $pdo->prepare('INSERT INTO jobs (job) VALUES (:job)');
                $stmt->execute([':job' => $input['job'] ?? '']);
                $newId = (int)$pdo->lastInsertId();

                $stmt = $pdo->prepare('SELECT * FROM jobs WHERE id = :id');
                $stmt->execute([':id' => $newId]);
                $job = $stmt->fetch();

                echo json_encode(['success' => true, 'job' => $job, 'id' => $newId]);
                exit;
            case 'PUT':
                if ($id <= 0) {
                    http_response_code(400);
                    echo json_encode(['success' => false, 'message' => 'Ungültige ID.']);
                    exit;
                }

                $stmt = $pdo->prepare('UPDATE jobs SET job = :job WHERE id = :id');
                $stmt->execute([':id' => $id, ':job' => $input['job'] ?? '']);
                echo json_encode(['success' => true, 'id' => $id]);
                exit;
            case 'DELETE':
                if ($id <= 0) {
                    http_response_code(400);
                    echo json_encode(['success' => false, 'message' => 'Ungültige ID.']);
                    exit;
                }

                $stmt = $pdo->prepare('DELETE FROM jobs WHERE id = :id');
                $stmt->execute([':id' => $id]);
                echo json_encode(['success' => true]);
                exit;
            default:
                http_response_code(405);
                echo json_encode(['success' => false, 'message' => 'Methode nicht erlaubt.']);
        }
    } catch (PDOException $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Datenbankfehler: ' . $e->getMessage()]);
    }
} catch (PDOException $e) {
    fail('Datenbankfehler: ' . $e->getMessage(), 500);
}