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
                    $stmt = $pdo->prepare('SELECT * FROM employee WHERE id = :id');
                    $stmt->execute([':id' => $id]);
                    $employee = $stmt->fetch();
                    echo json_encode(['success' => true, 'employee' => $employee ?: null]);
                    exit;
                }

                $stmt = $pdo->query('SELECT * FROM employee ORDER BY id ASC');
                $employees = $stmt->fetchAll();
                echo json_encode(['success' => true, 'employees' => $employees]);
                exit;
            case 'POST':
                $stmt = $pdo->prepare(
                    'INSERT INTO employee
                        (first_name, last_name, email, department, username, password, location_id, job_id, role_id, function_id)
                     VALUES
                        (:first_name, :last_name, :email, :department, :username, :password, :location_id, :job_id, :role_id, :function_id)'
                );

                $stmt->execute([
                    ':first_name' => $input['first_name'] ?? '',
                    ':last_name' => $input['last_name'] ?? '',
                    ':email' => $input['email'] ?? '',
                    ':department' => $input['department'] ?? '',
                    ':username' => $input['username'] ?? '',
                    ':password' => $input['password'] ?? '',
                    ':location_id' => isset($input['location_id']) ? (int)$input['location_id'] : 0,
                    ':job_id' => isset($input['job_id']) ? (int)$input['job_id'] : 0,
                    ':role_id' => isset($input['role_id']) ? (int)$input['role_id'] : 0,
                    ':function_id' => isset($input['function_id']) ? (int)$input['function_id'] : 0,
                ]);

                $newId = (int)$pdo->lastInsertId();
                $stmt = $pdo->prepare('SELECT * FROM employee WHERE id = :id');
                $stmt->execute([':id' => $newId]);
                $employee = $stmt->fetch();

                echo json_encode(['success' => true, 'employee' => $employee, 'id' => $newId]);
                exit;
            case 'PUT':
                if ($id <= 0) {
                    http_response_code(400);
                    echo json_encode(['success' => false, 'message' => 'Ungültige ID.']);
                    exit;
                }

                $stmt = $pdo->prepare(
                    'UPDATE employee SET
                        first_name = :first_name,
                        last_name = :last_name,
                        email = :email,
                        department = :department,
                        username = :username,
                        password = :password,
                        location_id = :location_id,
                        job_id = :job_id,
                        role_id = :role_id,
                        function_id = :function_id
                     WHERE id = :id'
                );

                $stmt->execute([
                    ':id' => $id,
                    ':first_name' => $input['first_name'] ?? '',
                    ':last_name' => $input['last_name'] ?? '',
                    ':email' => $input['email'] ?? '',
                    ':department' => $input['department'] ?? '',
                    ':username' => $input['username'] ?? '',
                    ':password' => $input['password'] ?? '',
                    ':location_id' => isset($input['location_id']) ? (int)$input['location_id'] : 0,
                    ':job_id' => isset($input['job_id']) ? (int)$input['job_id'] : 0,
                    ':role_id' => isset($input['role_id']) ? (int)$input['role_id'] : 0,
                    ':function_id' => isset($input['function_id']) ? (int)$input['function_id'] : 0,
                ]);

                echo json_encode(['success' => true, 'id' => $id]);
                exit;
            case 'DELETE':
                if ($id <= 0) {
                    http_response_code(400);
                    echo json_encode(['success' => false, 'message' => 'Ungültige ID.']);
                    exit;
                }

                $stmt = $pdo->prepare('DELETE FROM employee WHERE id = :id');
                $stmt->execute([':id' => $id]);

                echo json_encode(['success' => true]);
                exit;
            default:
                fail('Methode nicht erlaubt.', 405);
        }
    } catch (PDOException $e) {
        fail('Datenbankfehler: ' . $e->getMessage(), 500);
    }
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Datenbankfehler: ' . $e->getMessage()]);
}