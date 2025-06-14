from datetime import datetime, timezone
from time import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
import jwt
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Preferences
    preferred_cuisine = db.Column(db.String(64))
    dietary_restrictions = db.Column(db.String(256))  # Comma-separated values
    cooking_level = db.Column(db.String(32))  # beginner, intermediate, advanced
    location = db.Column(db.String(128))
    
    # Admin flag
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    recipes = db.relationship('Recipe', backref='author', lazy='dynamic')
    cooked_recipes = db.relationship('CookedRecipe', backref='user', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                          algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return f'<User {self.username}>'

class Recipe(db.Model):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    cook_time = db.Column(db.Integer)  # in minutes
    servings = db.Column(db.Integer)
    difficulty = db.Column(db.String(32))  # easy, medium, hard
    cuisine = db.Column(db.String(64))
    tags = db.Column(db.String(256))  # Comma-separated tags
    image_url = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    cooked_by = db.relationship('CookedRecipe', backref='recipe', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='recipe', lazy='dynamic')
    
    def __repr__(self):
        return f'<Recipe {self.title}>'

class CookedRecipe(db.Model):
    __tablename__ = 'cooked_recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    cooked_at = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Integer)  # 1-5 stars
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<CookedRecipe user_id={self.user_id} recipe_id={self.recipe_id}>'

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Favorite user_id={self.user_id} recipe_id={self.recipe_id}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
