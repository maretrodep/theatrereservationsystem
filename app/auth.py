import random
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from . import db
from .email_send import email_send
from datetime import datetime, timedelta

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.', 'danger')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists', 'danger')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='scrypt'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('main.index'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

@auth.route('/forgot-password', methods=['POST'])
def forgot_password_post():
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()

    if not user:
        flash('No account found with that email.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    # Generate a random reset code
    reset_code = str(random.randint(100000, 999999))

    # Set the expiration time (e.g., 15 minutes)
    reset_code_expiry = datetime.utcnow() + timedelta(minutes=15)

    # Store the reset code and its expiration in the database
    user.reset_code = reset_code
    user.reset_code_expiry = reset_code_expiry
    db.session.commit()

    # Use email_send function to send the code
    email_send([email], 'Password Reset Code', f'Your password reset code is: {reset_code}')
    flash('Password reset code sent to your email.', 'info')
    return redirect(url_for('auth.verify_reset_code'))



@auth.route('/verify-reset-code')
def verify_reset_code():
    return render_template('verify_reset_code.html')

@auth.route('/verify-reset-code', methods=['POST'])
def verify_reset_code_post():
    code = request.form.get('code')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # Check if the code is valid and not expired
    user = User.query.filter_by(reset_code=code).first()

    if not user or user.reset_code_expiry < datetime.utcnow():
        flash('Invalid or expired reset code.', 'danger')
        return redirect(url_for('auth.verify_reset_code'))

    if new_password != confirm_password:
        flash('Passwords do not match.', 'danger')
        return redirect(url_for('auth.verify_reset_code'))

    # Update the user's password
    user.password = generate_password_hash(new_password, method='scrypt')

    # Clear the reset code and expiry from the database
    user.reset_code = None
    user.reset_code_expiry = None
    db.session.commit()

    flash('Password reset successfully. You can now log in.', 'success')
    return redirect(url_for('auth.login'))



@auth.route('/change-password')
@login_required
def change_password():
    return render_template('change_password.html')

@auth.route('/change-password', methods=['POST'])
@login_required
def change_password_post():
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not check_password_hash(current_user.password, old_password):
        flash('Old password is incorrect.', 'danger')
        return redirect(url_for('auth.change_password'))

    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('auth.change_password'))

    # Update the user's password
    current_user.password = generate_password_hash(new_password, method='scrypt')
    db.session.commit()

    flash('Password changed successfully.', 'success')
    return redirect(url_for('main.index'))
