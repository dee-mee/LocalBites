from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])
    cuisine = SelectField('Cuisine', choices=[
        ('', 'All Cuisines'),
        ('kenyan', 'Kenyan'),
        ('indian', 'Indian'),
        ('western', 'Western'),
        ('chinese', 'Chinese'),
        ('italian', 'Italian'),
        ('other', 'Other')
    ], default='')
    difficulty = SelectField('Difficulty', choices=[
        ('', 'Any Level'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], default='')
    max_time = IntegerField('Max Time (min)', validators=[
        Optional(),
        NumberRange(min=1, max=240, message='Time must be between 1 and 240 minutes')
    ])
    ingredients = StringField('Ingredients (comma-separated)')
    vegetarian = BooleanField('Vegetarian')
    vegan = BooleanField('Vegan')
    submit = SubmitField('Search')

class RecipeForm(FlaskForm):
    title = StringField('Recipe Title', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Description')
    ingredients = TextAreaField('Ingredients (one per line)', validators=[DataRequired()])
    instructions = TextAreaField('Instructions', validators=[DataRequired()])
    cook_time = IntegerField('Cooking Time (minutes)', validators=[
        DataRequired(),
        NumberRange(min=1, max=1440, message='Time must be between 1 and 1440 minutes')
    ])
    servings = IntegerField('Servings', validators=[
        DataRequired(),
        NumberRange(min=1, max=100, message='Servings must be between 1 and 100')
    ])
    difficulty = SelectField('Difficulty Level', choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], validators=[DataRequired()])
    cuisine = SelectField('Cuisine', choices=[
        ('kenyan', 'Kenyan'),
        ('indian', 'Indian'),
        ('western', 'Western'),
        ('chinese', 'Chinese'),
        ('italian', 'Italian'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    tags = StringField('Tags (comma-separated)')
    is_vegetarian = BooleanField('Vegetarian')
    is_vegan = BooleanField('Vegan')
    is_gluten_free = BooleanField('Gluten Free')
    submit = SubmitField('Submit Recipe')
