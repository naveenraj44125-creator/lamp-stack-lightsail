<?php
require_once 'config/database.php';

try {
    $pdo = getDatabaseConnection();
    $stmt = $pdo->query('SELECT * FROM recipes ORDER BY created_at DESC');
    $recipes = $stmt->fetchAll();
} catch (Exception $e) {
    $recipes = [];
    $error = $e->getMessage();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recipe Manager - Docker + S3 Demo</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>🍳 Recipe Manager</h1>
            <p>Docker + AWS Lightsail Bucket Integration</p>
            <nav>
                <a href="/">Home</a>
                <a href="/admin/">Admin Panel</a>
                <a href="https://github.com/yourusername/lamp-stack-lightsail" target="_blank">GitHub</a>
            </nav>
        </div>
    </header>

    <main class="container">
        <?php if (isset($error)): ?>
        <div class="alert alert-error">
            <strong>Error:</strong> <?php echo htmlspecialchars($error); ?>
        </div>
        <?php endif; ?>

        <div class="hero">
            <h2>Discover Delicious Recipes</h2>
            <p>Browse our collection of recipes with images stored in AWS Lightsail buckets</p>
        </div>

        <div class="recipe-grid">
            <?php if (empty($recipes)): ?>
            <div class="empty-state">
                <h3>No recipes yet</h3>
                <p>Visit the <a href="/admin/">admin panel</a> to add your first recipe!</p>
            </div>
            <?php else: ?>
                <?php foreach ($recipes as $recipe): ?>
                <div class="recipe-card">
                    <?php if ($recipe['image_url']): ?>
                    <div class="recipe-image">
                        <img src="<?php echo htmlspecialchars($recipe['image_url']); ?>" 
                             alt="<?php echo htmlspecialchars($recipe['name']); ?>"
                             onerror="this.src='/assets/placeholder.jpg'">
                    </div>
                    <?php else: ?>
                    <div class="recipe-image placeholder">
                        <span>📷 No Image</span>
                    </div>
                    <?php endif; ?>
                    
                    <div class="recipe-content">
                        <h3><?php echo htmlspecialchars($recipe['name']); ?></h3>
                        <p class="recipe-description">
                            <?php echo htmlspecialchars(substr($recipe['description'], 0, 100)); ?>
                            <?php echo strlen($recipe['description']) > 100 ? '...' : ''; ?>
                        </p>
                        
                        <div class="recipe-meta">
                            <?php if ($recipe['category']): ?>
                            <span class="badge"><?php echo htmlspecialchars($recipe['category']); ?></span>
                            <?php endif; ?>
                            <span class="badge badge-<?php echo $recipe['difficulty']; ?>">
                                <?php echo ucfirst($recipe['difficulty']); ?>
                            </span>
                        </div>
                        
                        <div class="recipe-stats">
                            <?php if ($recipe['prep_time']): ?>
                            <span>⏱️ Prep: <?php echo $recipe['prep_time']; ?>min</span>
                            <?php endif; ?>
                            <?php if ($recipe['cook_time']): ?>
                            <span>🔥 Cook: <?php echo $recipe['cook_time']; ?>min</span>
                            <?php endif; ?>
                            <?php if ($recipe['servings']): ?>
                            <span>🍽️ Serves: <?php echo $recipe['servings']; ?></span>
                            <?php endif; ?>
                        </div>
                        
                        <button class="btn btn-primary" onclick="viewRecipe(<?php echo $recipe['id']; ?>)">
                            View Recipe
                        </button>
                    </div>
                </div>
                <?php endforeach; ?>
            <?php endif; ?>
        </div>
    </main>

    <!-- Recipe Modal -->
    <div id="recipeModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <div id="recipeDetails"></div>
        </div>
    </div>

    <footer>
        <div class="container">
            <p>&copy; 2024 Recipe Manager | Docker + AWS Lightsail Demo</p>
            <p>
                <a href="https://github.com/yourusername/lamp-stack-lightsail">View on GitHub</a> |
                <a href="/admin/">Admin Panel</a>
            </p>
        </div>
    </footer>

    <script src="/assets/js/app.js"></script>
</body>
</html>
