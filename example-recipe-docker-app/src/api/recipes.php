<?php
header('Content-Type: application/json');
require_once '../config/database.php';
require_once '../config/bucket.php';

$pdo = getDatabaseConnection();
$method = $_SERVER['REQUEST_METHOD'];

try {
    switch ($method) {
        case 'GET':
            if (isset($_GET['id'])) {
                // Get single recipe
                $stmt = $pdo->prepare('SELECT * FROM recipes WHERE id = ?');
                $stmt->execute([$_GET['id']]);
                $recipe = $stmt->fetch();
                
                if ($recipe) {
                    // Track view
                    $stmt = $pdo->prepare('INSERT INTO recipe_views (recipe_id, ip_address) VALUES (?, ?)');
                    $stmt->execute([$recipe['id'], $_SERVER['REMOTE_ADDR']]);
                    
                    echo json_encode(['success' => true, 'recipe' => $recipe]);
                } else {
                    http_response_code(404);
                    echo json_encode(['success' => false, 'error' => 'Recipe not found']);
                }
            } else {
                // Get all recipes
                $stmt = $pdo->query('SELECT * FROM recipes ORDER BY created_at DESC');
                $recipes = $stmt->fetchAll();
                echo json_encode(['success' => true, 'recipes' => $recipes, 'count' => count($recipes)]);
            }
            break;
            
        case 'DELETE':
            if (isset($_GET['id'])) {
                // Get recipe to delete image
                $stmt = $pdo->prepare('SELECT image_key FROM recipes WHERE id = ?');
                $stmt->execute([$_GET['id']]);
                $recipe = $stmt->fetch();
                
                if ($recipe && $recipe['image_key']) {
                    deleteImageFromBucket($recipe['image_key']);
                }
                
                // Delete recipe
                $stmt = $pdo->prepare('DELETE FROM recipes WHERE id = ?');
                $stmt->execute([$_GET['id']]);
                
                echo json_encode(['success' => true, 'message' => 'Recipe deleted']);
            } else {
                http_response_code(400);
                echo json_encode(['success' => false, 'error' => 'Recipe ID required']);
            }
            break;
            
        default:
            http_response_code(405);
            echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => $e->getMessage()]);
}
