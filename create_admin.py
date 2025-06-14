from app import create_app, db
from app.models import User

def create_admin(username, email, password):
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email=email).first()
        if admin:
            print(f"User with email {email} already exists. Updating to admin...")
            admin.is_admin = True
        else:
            print(f"Creating new admin user: {username}")
            admin = User(
                username=username,
                email=email,
                is_admin=True
            )
            admin.set_password(password)
            db.session.add(admin)
        
        db.session.commit()
        print("Admin user created/updated successfully!")

if __name__ == '__main__':
    import getpass
    
    print("Create Admin User")
    print("=================")
    username = input("Username: ")
    email = input("Email: ")
    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm Password: ")
    
    if password != confirm_password:
        print("Error: Passwords do not match!")
    else:
        create_admin(username, email, password)
