// Recipe Manager JavaScript

function viewRecipe(id) {
    fetch(`/api/recipes.php?id=${id}`)
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showRecipeModal(data.recipe);
            }
        });
}

function showRecipeModal(recipe) {
    const modal = document.getElementById('recipeModal');
    const details = document.getElementById('recipeDetails');
    
    const ingredients = recipe.ingredients.split('\n').map(i => `<li>${i}</li>`).join('');
    const instructions = recipe.instructions.split('\n').map((s, i) => `<li><strong>Step ${i+1}:</strong> ${s}</li>`).join('');
    
    details.innerHTML = `
        <h2>${recipe.name}</h2>
        ${recipe.image_url ? `<img src="${recipe.image_url}" alt="${recipe.name}" style="max-width: 100%; border-radius: 10px; margin: 20px 0;">` : ''}
        <p>${recipe.description || ''}</p>
        <div style="display: flex; gap: 20px; margin: 20px 0;">
            ${recipe.prep_time ? `<span>⏱️ Prep: ${recipe.prep_time}min</span>` : ''}
            ${recipe.cook_time ? `<span>🔥 Cook: ${recipe.cook_time}min</span>` : ''}
            ${recipe.servings ? `<span>🍽️ Serves: ${recipe.servings}</span>` : ''}
        </div>
        <h3>Ingredients</h3>
        <ul>${ingredients}</ul>
        <h3>Instructions</h3>
        <ol>${instructions}</ol>
    `;
    
    modal.style.display = 'block';
}

// Close modal
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('recipeModal');
    if (modal) {
        const closeBtn = modal.querySelector('.close');
        closeBtn.onclick = () => modal.style.display = 'none';
        window.onclick = (e) => {
            if (e.target === modal) modal.style.display = 'none';
        };
    }
});
