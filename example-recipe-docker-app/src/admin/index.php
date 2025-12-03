<?php
require_once '../config/database.php';
require_once '../config/session.php';

startSession();

// Simple auth check (in production, use proper authentication)
$isLoggedIn = isAdminLoggedIn();

if (!$isLoggedIn && $_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['login'])) {
    // Simple login (password: admin123)
    if ($_POST['username'] === 'admin' && $_POST['password'] === 'admin123') {
        loginAdmin('admin');
        $isLoggedIn = true;
        header('Location: /admin/');
        exit;
    } else {
        $loginError = 'Invalid credentials';
    }
}

if (isset($_GET['logout'])) {
    logoutAdmin();
    header('Location: /admin/');
    exit;
}

if ($isLoggedIn) {
    try {
        $pdo = getDatabaseConnection();
        $stmt = $pdo->query('SELECT * FROM recipes ORDER BY created_at DESC');
        $recipes = $stmt->fetchAll();
    } catch (Exception $e) {
        $recipes = [];
        $error = $e->getMessage();
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - Recipe Manager</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>🔐 Admin Panel</h1>
            <nav>
                <a href="/">Public Gallery</a>
                <?php if ($isLoggedIn): ?>
                <a href="/admin/upload.php">Upload Recipe</a>
                <a href="/admin/?logout=1">Logout</a>
                <?php endif; ?>
            </nav>
        </div>
    </header>

    <main class="container">
        <?php if (!$isLoggedIn): ?>
        <!-- Login Form -->
        <div class="login-container">
            <div class="login-box">
                <h2>Admin Login</h2>
                <?php if (isset($loginError)): ?>
                <div class="alert alert-error"><?php echo $loginError; ?></div>
                <?php endif; ?>
                <form method="POST">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" name="username" required value="admin">
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="password" required placeholder="admin123">
                    </div>
                    <button type="submit" name="login" class="btn btn-primary">Login</button>
                </form>
                <p class="hint">Default credentials: admin / admin123</p>
            </div>
        </div>
        <?php else: ?>
        <!-- Admin Dashboard -->
        <div class="admin-header">
            <h2>Recipe Management</h2>
            <a href="/admin/upload.php" class="btn btn-success">+ Add New Recipe</a>
        </div>

        <?php if (isset($error)): ?>
        <div class="alert alert-error"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>

        <div class="admin-table">
            <table>
                <thead>
                    <tr>
                        <th>Image</th>
                        <th>Name</th>
                        <th>Category</th>
                        <th>Difficulty</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (empty($recipes)): ?>
                    <tr>
                        <td colspan="6" class="text-center">No recipes found. <a href="/admin/upload.php">Add one now!</a></td>
                    </tr>
                    <?php else: ?>
                        <?php foreach ($recipes as $recipe): ?>
                        <tr>
                            <td>
                                <?php if ($recipe['image_url']): ?>
                                <img src="<?php echo htmlspecialchars($recipe['image_url']); ?>" 
                                     alt="<?php echo htmlspecialchars($recipe['name']); ?>"
                                     class="table-thumb">
                                <?php else: ?>
                                <span class="no-image">📷</span>
                                <?php endif; ?>
                            </td>
                            <td><strong><?php echo htmlspecialchars($recipe['name']); ?></strong></td>
                            <td><?php echo htmlspecialchars($recipe['category'] ?: '-'); ?></td>
                            <td><span class="badge badge-<?php echo $recipe['difficulty']; ?>"><?php echo ucfirst($recipe['difficulty']); ?></span></td>
                            <td><?php echo date('M d, Y', strtotime($recipe['created_at'])); ?></td>
                            <td>
                                <button onclick="editRecipe(<?php echo $recipe['id']; ?>)" class="btn btn-sm">Edit</button>
                                <button onclick="deleteRecipe(<?php echo $recipe['id']; ?>)" class="btn btn-sm btn-danger">Delete</button>
                            </td>
                        </tr>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>
        <?php endif; ?>
    </main>

    <script src="/assets/js/app.js"></script>
    <script>
        function editRecipe(id) {
            window.location.href = '/admin/upload.php?id=' + id;
        }

        function deleteRecipe(id) {
            if (confirm('Are you sure you want to delete this recipe?')) {
                fetch('/api/recipes.php?id=' + id, {
                    method: 'DELETE'
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Error: ' + data.error);
                    }
                });
            }
        }
    </script>
</body>
</html>
