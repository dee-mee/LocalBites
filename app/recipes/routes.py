from flask import render_template, flash, redirect, url_for, request, current_app, abort
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os
from app import db
from app.recipes import bp
from app.models import Recipe, CookedRecipe, Favorite, User
from app.main.forms import RecipeForm
from datetime import datetime

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = RecipeForm()
    if form.validate_on_submit():
        # Process tags
        tags = []
        if form.is_vegetarian.data:
            tags.append('vegetarian')
        if form.is_vegan.data:
            tags.append('vegan')
        if form.is_gluten_free.data:
            tags.append('gluten-free')
        if form.tags.data:
            tags.extend([tag.strip() for tag in form.tags.data.split(',')])
        
        # Create recipe
        recipe = Recipe(
            title=form.title.data,
            description=form.description.data,
            ingredients=form.ingredients.data,
            instructions=form.instructions.data,
            cook_time=form.cook_time.data,
            servings=form.servings.data,
            difficulty=form.difficulty.data,
            cuisine=form.cuisine.data,
            tags=','.join(tags),
            author=current_user
        )
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                recipe.image_url = f'uploads/{filename}'
        
        db.session.add(recipe)
        db.session.commit()
        flash('Your recipe has been created!', 'success')
        return redirect(url_for('recipes.recipe', id=recipe.id))
    
    return render_template('recipes/create.html', title='Create Recipe', form=form)

@bp.route('/recipe/<int:id>')
def recipe(id):
    recipe = Recipe.query.get_or_404(id)
    return render_template('recipes/recipe.html', recipe=recipe)

@bp.route('/recipe/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    if recipe.author != current_user:
        abort(403)
    
    form = RecipeForm()
    if form.validate_on_submit():
        # Process tags
        tags = []
        if form.is_vegetarian.data:
            tags.append('vegetarian')
        if form.is_vegan.data:
            tags.append('vegan')
        if form.is_gluten_free.data:
            tags.append('gluten-free')
        if form.tags.data:
            tags.extend([tag.strip() for tag in form.tags.data.split(',')])
        
        # Update recipe
        recipe.title = form.title.data
        recipe.description = form.description.data
        recipe.ingredients = form.ingredients.data
        recipe.instructions = form.instructions.data
        recipe.cook_time = form.cook_time.data
        recipe.servings = form.servings.data
        recipe.difficulty = form.difficulty.data
        recipe.cuisine = form.cuisine.data
        recipe.tags = ','.join(tags)
        recipe.updated_at = datetime.utcnow()
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # Delete old image if exists
                if recipe.image_url:
                    try:
                        os.remove(os.path.join(current_app.static_folder, recipe.image_url))
                    except OSError:
                        pass
                
                # Save new image
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                recipe.image_url = f'uploads/{filename}'
        
        db.session.commit()
        flash('Your recipe has been updated!', 'success')
        return redirect(url_for('recipes.recipe', id=recipe.id))
    
    elif request.method == 'GET':
        form.title.data = recipe.title
        form.description.data = recipe.description
        form.ingredients.data = recipe.ingredients
        form.instructions.data = recipe.instructions
        form.cook_time.data = recipe.cook_time
        form.servings.data = recipe.servings
        form.difficulty.data = recipe.difficulty
        form.cuisine.data = recipe.cuisine
        
        # Set boolean fields
        tags = recipe.tags.split(',') if recipe.tags else []
        form.is_vegetarian.data = 'vegetarian' in tags
        form.is_vegan.data = 'vegan' in tags
        form.is_gluten_free.data = 'gluten-free' in tags
        
        # Set other tags
        other_tags = [tag for tag in tags if tag not in 
                     ['vegetarian', 'vegan', 'gluten-free']]
        form.tags.data = ', '.join(other_tags)
    
    return render_template('recipes/edit_recipe.html', title='Edit Recipe', 
                         form=form, recipe=recipe)

@bp.route('/recipe/<int:id>/delete', methods=['POST'])
@login_required
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    if recipe.author != current_user:
        abort(403)
    
    # Delete associated image if exists
    if recipe.image_url:
        try:
            os.remove(os.path.join(current_app.static_folder, recipe.image_url))
        except OSError:
            pass
    
    db.session.delete(recipe)
    db.session.commit()
    flash('Your recipe has been deleted!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/recipe/<int:id>/cook', methods=['POST'])
@login_required
def cook_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    cooked = CookedRecipe(user_id=current_user.id, recipe_id=recipe.id)
    db.session.add(cooked)
    db.session.commit()
    flash(f'You cooked {recipe.title}!', 'success')
    return redirect(url_for('recipes.recipe', id=recipe.id))

@bp.route('/recipe/<int:id>/favorite', methods=['POST'])
@login_required
def favorite_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    favorite = Favorite.query.filter_by(
        user_id=current_user.id, recipe_id=recipe.id).first()
    
    if favorite:
        db.session.delete(favorite)
        action = 'removed from'
    else:
        favorite = Favorite(user_id=current_user.id, recipe_id=recipe.id)
        db.session.add(favorite)
        action = 'added to'
    
    db.session.commit()
    flash(f'Recipe {action} your favorites!', 'success')
    return redirect(url_for('recipes.recipe', id=recipe.id))

@bp.route('/saved')
@login_required
def saved_recipes():
    # Get all favorite recipes for the current user
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    # Extract the recipe IDs from favorites
    recipe_ids = [f.recipe_id for f in favorites]
    # Get the actual recipe objects
    saved_recipes = Recipe.query.filter(Recipe.id.in_(recipe_ids)).all()
    
    return render_template('recipes/saved_recipes.html', 
                         title='Saved Recipes',
                         saved_recipes=saved_recipes)
