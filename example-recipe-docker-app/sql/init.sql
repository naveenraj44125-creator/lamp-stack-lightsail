-- Recipe Manager Database Schema

CREATE TABLE IF NOT EXISTS recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    ingredients TEXT NOT NULL,
    instructions TEXT NOT NULL,
    prep_time INT,  -- in minutes
    cook_time INT,  -- in minutes
    servings INT DEFAULT 1,
    difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
    category VARCHAR(50),
    image_key VARCHAR(255),  -- S3 bucket key for the image
    image_url TEXT,  -- Full S3 URL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_difficulty (difficulty),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sample recipes
INSERT INTO recipes (name, description, ingredients, instructions, prep_time, cook_time, servings, difficulty, category) VALUES
('Classic Spaghetti Carbonara', 'Traditional Italian pasta dish with eggs, cheese, and bacon', 
 '400g spaghetti\n200g pancetta or bacon\n4 large eggs\n100g Parmesan cheese\nBlack pepper\nSalt',
 '1. Cook spaghetti in salted boiling water\n2. Fry pancetta until crispy\n3. Beat eggs with grated Parmesan\n4. Drain pasta, mix with pancetta\n5. Remove from heat, add egg mixture\n6. Toss quickly, season with pepper',
 10, 15, 4, 'easy', 'Italian'),

('Chocolate Chip Cookies', 'Soft and chewy homemade cookies', 
 '2 1/4 cups flour\n1 tsp baking soda\n1 tsp salt\n1 cup butter\n3/4 cup sugar\n3/4 cup brown sugar\n2 eggs\n2 tsp vanilla\n2 cups chocolate chips',
 '1. Preheat oven to 375°F\n2. Mix flour, baking soda, salt\n3. Beat butter and sugars\n4. Add eggs and vanilla\n5. Stir in flour mixture\n6. Fold in chocolate chips\n7. Drop spoonfuls on baking sheet\n8. Bake 9-11 minutes',
 15, 10, 48, 'easy', 'Dessert'),

('Thai Green Curry', 'Spicy and aromatic Thai curry with vegetables', 
 '2 tbsp green curry paste\n400ml coconut milk\n300g chicken breast\n1 cup vegetables (bell peppers, bamboo shoots)\n2 tbsp fish sauce\n1 tbsp sugar\nBasil leaves\nJasmine rice',
 '1. Heat oil, fry curry paste\n2. Add coconut milk, bring to simmer\n3. Add chicken, cook 10 minutes\n4. Add vegetables, cook 5 minutes\n5. Season with fish sauce and sugar\n6. Garnish with basil\n7. Serve with rice',
 15, 20, 4, 'medium', 'Thai'),

('Caesar Salad', 'Classic Caesar salad with homemade dressing', 
 '1 large romaine lettuce\n1/2 cup Caesar dressing\n1/2 cup croutons\n1/4 cup Parmesan cheese\n2 anchovy fillets (optional)',
 '1. Wash and chop romaine lettuce\n2. Make dressing: blend anchovies, garlic, lemon juice, Dijon mustard, egg yolk, olive oil\n3. Toss lettuce with dressing\n4. Add croutons and Parmesan\n5. Serve immediately',
 10, 0, 4, 'easy', 'Salad');

-- Admin users table (simple auth)
CREATE TABLE IF NOT EXISTS admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Default admin user (password: admin123)
INSERT INTO admin_users (username, password_hash, email) VALUES
('admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin@recipe-app.com');

-- Recipe views tracking
CREATE TABLE IF NOT EXISTS recipe_views (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    INDEX idx_recipe_id (recipe_id),
    INDEX idx_viewed_at (viewed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SELECT 'Recipe Manager database initialized successfully!' AS message;
