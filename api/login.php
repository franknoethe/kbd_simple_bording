<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Nur POST erlaubt.']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);

$username = trim((string)($input['username'] ?? ''));
$password = trim((string)($input['password'] ?? ''));

if ($username === '' || $password === '') {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Benutzer und Passwort sind erforderlich.']);
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

    $stmt = $pdo->prepare(
        'SELECT username, role_id FROM employee WHERE username = :username AND `password` = :password LIMIT 1'
    );

    $stmt->execute([
        ':username' => $username,
        ':password' => $password
    ]);

    $row = $stmt->fetch();

    if ($row) {
        echo json_encode([
            'success' => true,
            'user' => [
                'username' => $row['username'],
                'role_id' => (int)$row['role_id']
            ]
        ]);
    } else {
        echo json_encode([
            'success' => false,
            'message' => 'Benutzername oder Passwort ungültig.'
        ]);
    }
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Datenbankfehler: ' . $e->getMessage()
    ]);
}