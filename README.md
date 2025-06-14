# LocalBites

A recipe sharing and discovery platform that connects food enthusiasts with local flavors and culinary experiences.

## Features

- **User Authentication**: Register, login, and manage user profiles
- **Recipe Management**: Create, edit, and delete recipes
- **Recipe Discovery**: Browse and search for recipes
- **Personal Collections**: Save favorite recipes and track cooked meals
- **User Profiles**: Showcase your culinary journey and preferences
- **Admin Dashboard**: Manage users, recipes, and view statistics

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Database**: SQLite (development), SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Form Handling**: Flask-WTF
- **Email Support**: Flask-Mail
- **Date/Time Handling**: Flask-Moment
- **Database Migrations**: Flask-Migrate

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dee-mee/LocalBites.git
   cd LocalBites
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your configuration.

5. Initialize the database:
   ```bash
   flask db upgrade
   ```

6. Create an admin user:
   ```bash
   python create_admin.py
   ```

### Running the Application

```bash
flask run
```

Visit `http://localhost:5000` in your browser.

## Project Structure

```
LocalBites/
├── app/
│   ├── __init__.py         # Application factory and extensions
│   ├── models.py           # Database models
│   ├── auth/               # Authentication routes and forms
│   ├── main/               # Main application routes
│   ├── recipes/            # Recipe-related routes
│   ├── admin/              # Admin routes
│   └── templates/          # HTML templates
├── migrations/             # Database migrations
├── config.py               # Configuration settings
├── requirements.txt        # Project dependencies
└── run.py                  # Application entry point
```

## Database Models

- **User**: Stores user information and preferences
- **Recipe**: Contains recipe details and metadata
- **CookedRecipe**: Tracks when users cook recipes
- **Favorite**: Manages user's favorite recipes

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `POST /auth/reset_password_request` - Request password reset
- `POST /auth/reset_password/<token>` - Reset password with token

### Recipes
- `GET /` - View all recipes
- `GET /recipes/<id>` - View a specific recipe
- `GET /recipes/create` - Create a new recipe (authenticated)
- `POST /recipes/create` - Save a new recipe (authenticated)
- `GET /recipes/edit/<id>` - Edit a recipe (owner only)
- `POST /recipes/edit/<id>` - Update a recipe (owner only)
- `POST /recipes/delete/<id>` - Delete a recipe (owner only)
- `POST /recipes/<id>/cooked` - Mark recipe as cooked
- `POST /recipes/<id>/favorite` - Add to favorites

### User Profiles
- `GET /user/<username>` - View user profile
- `GET /user/edit_profile` - Edit profile (authenticated)
- `POST /user/edit_profile` - Update profile (authenticated)

### Admin
- `GET /admin/` - Admin dashboard
- `GET /admin/users` - Manage users
- `GET /admin/recipes` - Manage recipes
- `GET /admin/statistics` - View statistics

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Styled with [Bootstrap](https://getbootstrap.com/)
- Icons from [Font Awesome](https://fontawesome.com/)
