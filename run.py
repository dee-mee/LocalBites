from app import create_app, db
from app.models import User, Recipe, CookedRecipe, Favorite

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Recipe': Recipe, 
            'CookedRecipe': CookedRecipe, 'Favorite': Favorite}

if __name__ == '__main__':
    app.run(debug=True)
