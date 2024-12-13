from werkzeug.security import generate_password_hash
from app import db, create_app  # Adjust the import based on your Flask app structure
from app.models import User  # Adjust the import based on your models location

app = create_app()


def add_owner_and_admin():
    """
    Adds an owner and an admin to the database if they don't already exist.
    """
    # Define owner details
    owner_email = "owner@example.com"
    owner_password = "123"
    owner_name = "Pedram Akbari"

    # Define admin details
    admin_email = "admin@example.com"
    admin_password = "123"
    admin_name = "Pedram Akbari"

    with app.app_context():
        hashed_password = generate_password_hash(owner_password, method='scrypt')
        new_owner = User(email=owner_email, name=owner_name, password=hashed_password, role='owner')
        db.session.add(new_owner)

        hashed_password = generate_password_hash(admin_password, method='scrypt')
        new_admin = User(email=admin_email, name=admin_name, password=hashed_password, role='admin')
        db.session.add(new_admin)

        # Commit changes to the database
        db.session.commit()
        print("Owner and admin have been added (if they didn't already exist).")

if __name__ == '__main__':
    add_owner_and_admin()