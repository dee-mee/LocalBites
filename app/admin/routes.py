from flask import render_template, redirect, url_for, flash, request, current_app, abort, jsonify
from flask_login import login_required, current_user, logout_user
from app.admin import bp
from app.models import User, Recipe, CookedRecipe, Favorite
from app import db
from datetime import datetime, timedelta
import os

@bp.before_request
@login_required
def require_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

@bp.route('/admin')
@login_required
def index():
    # Admin dashboard
    total_users = User.query.count()
    total_recipes = Recipe.query.count()
    recent_users = User.query.order_by(User.member_since.desc()).limit(5).all()
    recent_recipes = Recipe.query.order_by(Recipe.created_at.desc()).limit(5).all()
    
    # Get more statistics
    active_users = User.query.filter(
        User.last_seen > (datetime.utcnow() - timedelta(days=7))
    ).count()
    
    popular_recipes = Recipe.query.outerjoin(CookedRecipe).group_by(Recipe.id).order_by(
        db.func.count(CookedRecipe.id).desc()
    ).limit(5).all()
    
    return render_template('admin/index.html',
                         title='Admin Dashboard',
                         total_users=total_users,
                         total_recipes=total_recipes,
                         recent_users=recent_users,
                         recent_recipes=recent_recipes,
                         active_users=active_users,
                         popular_recipes=popular_recipes)

@bp.route('/admin/users')
@login_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    query = User.query
    
    # Search functionality
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) | 
            (User.email.ilike(f'%{search}%'))
        )
    
    # Filter by user type
    user_type = request.args.get('type', 'all')
    if user_type == 'admin':
        query = query.filter_by(is_admin=True)
    elif user_type == 'regular':
        query = query.filter_by(is_admin=False)
    
    # Ordering
    order_by = request.args.get('order_by', 'username')
    if order_by == 'recent':
        query = query.order_by(User.member_since.desc())
    else:
        query = query.order_by(User.username.asc())
    
    users = query.paginate(
        page=page, 
        per_page=current_app.config['POSTS_PER_PAGE'], 
        error_out=False
    )
    
    return render_template('admin/users.html', 
                         title='Manage Users', 
                         users=users,
                         search=search,
                         user_type=user_type,
                         order_by=order_by)

@bp.route('/admin/recipes')
@login_required
def manage_recipes():
    page = request.args.get('page', 1, type=int)
    query = Recipe.query
    
    # Search functionality
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            (Recipe.title.ilike(f'%{search}%')) | 
            (Recipe.description.ilike(f'%{search}%'))
        )
    
    # Filter by status
    status = request.args.get('status', 'all')
    if status == 'recent':
        week_ago = datetime.utcnow() - timedelta(days=7)
        query = query.filter(Recipe.created_at >= week_ago)
    
    # Ordering
    order_by = request.args.get('order_by', 'recent')
    if order_by == 'popular':
        query = query.outerjoin(CookedRecipe).group_by(Recipe.id).order_by(
            db.func.count(CookedRecipe.id).desc()
        )
    elif order_by == 'title':
        query = query.order_by(Recipe.title.asc())
    else:  # recent
        query = query.order_by(Recipe.created_at.desc())
    
    recipes = query.paginate(
        page=page, 
        per_page=current_app.config['POSTS_PER_PAGE'], 
        error_out=False
    )
    
    return render_template('admin/recipes.html', 
                         title='Manage Recipes', 
                         recipes=recipes,
                         search=search,
                         status=status,
                         order_by=order_by)

@bp.route('/admin/user/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
def toggle_admin(user_id):
    if not current_user.is_admin:
        abort(403)
        
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot modify your own admin status', 'danger')
    else:
        user.is_admin = not user.is_admin
        action = 'promoted to admin' if user.is_admin else 'demoted from admin'
        db.session.commit()
        flash(f'User {user.username} has been {action}', 'success')
    
    return redirect(request.referrer or url_for('admin.manage_users'))

@bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
        
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot delete your own account from here', 'danger')
    else:
        # Delete user's recipes, favorites, etc.
        for recipe in user.recipes:
            # Delete recipe image if exists
            if recipe.image_url and recipe.image_url != 'default.jpg':
                try:
                    os.remove(os.path.join(current_app.static_folder, recipe.image_url))
                except OSError:
                    pass
            db.session.delete(recipe)
        
        # Delete user's favorites
        Favorite.query.filter_by(user_id=user.id).delete()
        
        # Delete user's cooked recipes
        CookedRecipe.query.filter_by(user_id=user.id).delete()
        
        # Finally, delete the user
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} has been deleted', 'success')
    
    return redirect(url_for('admin.manage_users'))

@bp.route('/admin/recipe/<int:recipe_id>/delete', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    if not current_user.is_admin:
        abort(403)
        
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # Delete recipe image if exists
    if recipe.image_url and recipe.image_url != 'default.jpg':
        try:
            os.remove(os.path.join(current_app.static_folder, recipe.image_url))
        except OSError:
            pass
    
    # Delete associated favorites and cooked records
    Favorite.query.filter_by(recipe_id=recipe.id).delete()
    CookedRecipe.query.filter_by(recipe_id=recipe.id).delete()
    
    db.session.delete(recipe)
    db.session.commit()
    flash(f'Recipe "{recipe.title}" has been deleted', 'success')
    
    return redirect(request.referrer or url_for('admin.manage_recipes'))

@bp.route('/admin/statistics')
@login_required
def statistics():
    if not current_user.is_admin:
        abort(403)
    
    # User statistics
    total_users = User.query.count()
    new_users_this_week = User.query.filter(
        User.member_since > (datetime.utcnow() - timedelta(days=7))
    ).count()
    
    # Recipe statistics
    total_recipes = Recipe.query.count()
    new_recipes_this_week = Recipe.query.filter(
        Recipe.created_at > (datetime.utcnow() - timedelta(days=7))
    ).count()
    
    # Popular recipes
    popular_recipes = Recipe.query.outerjoin(CookedRecipe).group_by(Recipe.id).order_by(
        db.func.count(CookedRecipe.id).desc()
    ).limit(5).all()
    
    # Activity statistics
    active_users = User.query.filter(
        User.last_seen > (datetime.utcnow() - timedelta(days=1))
    ).count()
    
    return render_template('admin/statistics.html',
                         title='Statistics',
                         total_users=total_users,
                         new_users_this_week=new_users_this_week,
                         total_recipes=total_recipes,
                         new_recipes_this_week=new_recipes_this_week,
                         popular_recipes=popular_recipes,
                         active_users=active_users)
