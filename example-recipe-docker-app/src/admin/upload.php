<?php
require_once '../config/database.php';
require_once '../config/bucket.php';
require_once '../config/session.php';

requireAdmin();

$pdo = getDatabaseConnection();
$recipe = null;
$isEdit = false;

// Load recipe for editing
if (isset($_GET['id'])) {
    $stmt = $pdo->prepare('SELECT * FROM recipes WHERE id = ?');
    $stmt->execute([$_GET['id']]);
    $recipe = $stmt->fetch();
    $isEdit = true;
}

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = $_POST['name'];
    $description = $_POST['description'];
    $ingredients = $_POST['ingredients'];
    $instructions = $_POST['instructions'];
    $prep_time = $_POST['prep_time'] ?: null;
    $cook_time = $_POST['cook_time'] ?: null;
    $servings = $_POST['servings'] ?: 1;
    $difficulty = $_POST['difficulty'];
    $category = $_POST['category'];
    
    $imageKey = $recipe['image_key'] ?? null;
    $imageUrl = $recipe['image_url'] ?? null;
    
    // Handle image upload
    if (isset($_FILES['image']) && $_FILES['image']['error'] === UPLOAD_ERR_OK) {
        $validation = validateImageFile($_FILES['image']);
        if ($validation['valid']) {
            $filename = generateUniqueFilename($_FILES['image']['name']);
            $uploadResult = uploadImageToBucket($_FILES['image'], $filename);
            
            if ($uploadResult['success']) {
                // Delete old image if exists
                if ($imageKey) {
                    deleteImageFromBucket($imageKey);
                }
                $imageKey = $uploadResult['key'];
                $imageUrl = $uploadResult['url'];
            }
        }
    }
    
    if ($isEdit) {
        $stmt = $pdo->prepare('UPDATE recipes SET name=?, description=?, ingredients=?, instructions=?, prep_time=?, cook_time=?, servings=?, difficulty=?, category=?, image_key=?, image_url=? WHERE id=?');
        $stmt->execute([$name, $description, $ingredients, $instructions, $prep_time, $cook_time, $servings, $difficulty, $category, $imageKey, $imageUrl, $_GET['id']]);
    } else {
        $stmt = $pdo->prepare('INSERT INTO recipes (name, description, ingredients, instructions, prep_time, cook_time, servings, difficulty, category, image_key, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)');
        $stmt->execute([$name, $description, $ingredients, $instructions, $prep_time, $cook_time, $servings, $difficulty, $category, $imageKey, $imageUrl]);
    }
    
    header('Location: /admin/');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $isEdit ? 'Edit' : 'Add'; ?> Recipe - Admin</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1><?php echo $isEdit ? '✏️ Edit' : '➕ Add'; ?> Recipe</h1>
            <nav>
                <a href="/admin/">Back to Admin</a>
                <a href="/">Public Gallery</a>
            </nav>
        </div>
    </header>

    <main class="container">
        <form method="POST" enctype="multipart/form-data" class="recipe-form">
            <div class="form-group">
                <label>Recipe Name *</label>
                <input type="text" name="name" required value="<?php echo htmlspecialchars($recipe['name'] ?? ''); ?>">
            </div>

            <div class="form-group">
                <label>Description</label>
                <textarea name="description" rows="3"><?php echo htmlspecialchars($recipe['description'] ?? ''); ?></textarea>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Category</label>
                    <input type="text" name="category" value="<?php echo htmlspecialchars($recipe['category'] ?? ''); ?>" placeholder="e.g., Italian, Dessert">
                </div>
                <div class="form-group">
                    <label>Difficulty *</label>
                    <select name="difficulty" required>
                        <option value="easy" <?php echo ($recipe['difficulty'] ?? '') === 'easy' ? 'selected' : ''; ?>>Easy</option>
                        <option value="medium" <?php echo ($recipe['difficulty'] ?? 'medium') === 'medium' ? 'selected' : ''; ?>>Medium</option>
                        <option value="hard" <?php echo ($recipe['difficulty'] ?? '') === 'hard' ? 'selected' : ''; ?>>Hard</option>
                    </select>
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Prep Time (minutes)</label>
                    <input type="number" name="prep_time" value="<?php echo $recipe['prep_time'] ?? ''; ?>">
                </div>
                <div class="form-group">
                    <label>Cook Time (minutes)</label>
                    <input type="number" name="cook_time" value="<?php echo $recipe['cook_time'] ?? ''; ?>">
                </div>
                <div class="form-group">
                    <label>Servings</label>
                    <input type="number" name="servings" value="<?php echo $recipe['servings'] ?? '1'; ?>">
                </div>
            </div>

            <div class="form-group">
                <label>Ingredients * (one per line)</label>
                <textarea name="ingredients" rows="8" required><?php echo htmlspecialchars($recipe['ingredients'] ?? ''); ?></textarea>
            </div>

            <div class="form-group">
                <label>Instructions * (one step per line)</label>
                <textarea name="instructions" rows="10" required><?php echo htmlspecialchars($recipe['instructions'] ?? ''); ?></textarea>
            </div>

            <div class="form-group">
                <label>Recipe Image (JPG, PNG, GIF - Max 5MB)</label>
                <?php if ($recipe['image_url'] ?? null): ?>
                <div class="current-image">
                    <img src="<?php echo htmlspecialchars($recipe['image_url']); ?>" alt="Current image">
                    <p>Current image (upload new to replace)</p>
                </div>
                <?php endif; ?>
                <input type="file" name="image" accept="image/*">
            </div>

            <div class="form-actions">
                <button type="submit" class="btn btn-success"><?php echo $isEdit ? 'Update' : 'Create'; ?> Recipe</button>
                <a href="/admin/" class="btn">Cancel</a>
            </div>
        </form>
    </main>
</body>
</html>
