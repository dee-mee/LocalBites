from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models import Recipe, User, CookedRecipe
from app.main.forms import SearchForm

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        current_app.jinja_env.globals['search_form'] = SearchForm()

@bp.route('/')
@bp.route('/index')
def index():
    # Get popular recipes (example: most cooked)
    popular_recipes = Recipe.query.join(
        CookedRecipe, Recipe.id == CookedRecipe.recipe_id
    ).group_by(Recipe.id).order_by(
        db.func.count(CookedRecipe.id).desc()
    ).limit(6).all()
    
    # Get recently added recipes
    recent_recipes = Recipe.query.order_by(Recipe.created_at.desc()).limit(6).all()
    
    return render_template('index.html', 
                         title='Home',
                         popular_recipes=popular_recipes,
                         recent_recipes=recent_recipes)

@bp.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    recipes = Recipe.query.order_by(Recipe.created_at.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.explore', page=recipes.next_num) if recipes.has_next else None
    prev_url = url_for('main.explore', page=recipes.prev_num) if recipes.has_prev else None
    return render_template('recipes/explore.html', 
                         title='Explore',
                         recipes=recipes.items,
                         next_url=next_url,
                         prev_url=prev_url)

@bp.route('/search')
def search():
    if not current_app.jinja_env.globals.get('search_form', None):
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '')
    
    if not query:
        flash('Please enter a search term', 'warning')
        return redirect(url_for('main.index'))
    
    # Basic search in title, ingredients, and tags
    search = f"%{query}%"
    recipes = Recipe.query.filter(
        (Recipe.title.ilike(search)) |
        (Recipe.ingredients.ilike(search)) |
        (Recipe.tags.ilike(search))
    ).order_by(Recipe.created_at.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    
    next_url = url_for('main.search', q=query, page=recipes.next_num) if recipes.has_next else None
    prev_url = url_for('main.search', q=query, page=recipes.prev_num) if recipes.has_prev else None
    
    return render_template('search.html',
                         title='Search Results',
                         query=query,
                         recipes=recipes.items,
                         next_url=next_url,
                         prev_url=prev_url)
