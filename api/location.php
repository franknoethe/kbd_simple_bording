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

    if ($method === 'GET') {
        $stmt = $pdo->query('SELECT id, location FROM locations ORDER BY id ASC');
        $rows = $stmt->fetchAll();

        echo json_encode([
            'success' => true,
            'locations' => $rows
        ]);
        exit;
    }

    $input = json_decode(file_get_contents('php://input'), true);

    if ($method === 'POST') {
        $location = trim((string)($input['location'] ?? ''));

        if ($location === '') {
            http_response_code(400);
            echo json_encode([
                'success' => false,
                'message' => 'Standort darf nicht leer sein.'
            ]);
            exit;
        }

        $stmt = $pdo->prepare('INSERT INTO locations (location) VALUES (:location)');
        $stmt->execute([':location' => $location]);

        echo json_encode([
            'success' => true,
            'location' => [
                'id' => (int)$pdo->lastInsertId(),
                'location' => $location
            ]
        ]);
        exit;
    }

    if ($method === 'PUT') {
        $id = (int)($input['id'] ?? 0);
        $location = trim((string)($input['location'] ?? ''));

        if ($id <= 0 || $location === '') {
            http_response_code(400);
            echo json_encode([
                'success' => false,
                'message' => 'Ungültige Daten für die Änderung.'
            ]);
            exit;
        }

        $stmt = $pdo->prepare('UPDATE locations SET location = :location WHERE id = :id');
        $stmt->execute([
            ':location' => $location,
            ':id' => $id
        ]);

        echo json_encode([
            'success' => true,
            'location' => [
                'id' => $id,
                'location' => $location
            ]
        ]);
        exit;
    }

    if ($method === 'DELETE') {
        $id = (int)($input['id'] ?? 0);

        if ($id <= 0) {
            http_response_code(400);
            echo json_encode([
                'success' => false,
                'message' => 'Ungültige ID zum Löschen.'
            ]);
            exit;
        }

        $stmt = $pdo->prepare('DELETE FROM locations WHERE id = :id');
        $stmt->execute([':id' => $id]);

        echo json_encode([
            'success' => true,
            'message' => 'Standort gelöscht.'
        ]);
        exit;
    }

    http_response_code(405);
    echo json_encode([
        'success' => false,
        'message' => 'Methode nicht erlaubt.'
    ]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'Datenbankfehler: ' . $e->getMessage()
    ]);
}