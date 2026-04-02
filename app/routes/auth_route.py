from flask import request, redirect, url_for, render_template, flash, Blueprint, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint("auth", __name__)
@auth.route('/skinDisease')
def skinDisease():
    return render_template("diseasetype.html")


    
# --- REGISTER / SIGNUP ---
@auth.route('/signup', methods=['POST', 'GET']) # Path '/' se '/signup' kar diya taaki confusion na ho
def signup():
    # Agar user pehle se login hai, toh usse wapas registration page mat dikhao
    if current_user.is_authenticated:
        return redirect(url_for('upload.index')) # Dashboard pe redirect kar do

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Security Update: 'scrypt' method password hashing ke liye best hai
        hashed_password = generate_password_hash(password, method='scrypt')
        
        # Check user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already Registered!", "danger")
            return redirect(url_for('auth.signup'))

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration Successful!", "success") # 'Success' ko 'success' (lowercase) kiya CSS ke liye
        return redirect(url_for('auth.login'))
        
    return render_template('signup.html') # File name update

# --- LOGIN ---
@auth.route("/login", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('upload.index')) # Agar already login hai toh upload page pe bhej do

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user) # Flask-Login automatic session handle karega
            
            
            flash(f'You Successfully Logged In, {user.username}!', 'success')
            return redirect(url_for('upload.index'))
        
        flash("Oops! Wrong Email or Password!", 'danger')
        return redirect(url_for('auth.login'))
        
    return render_template('login.html')

# --- LOGOUT ---
@auth.route('/logout')
@login_required # Sirf login user hi logout hit kar sake
def logout():
    logout_user() # Flask-Login ka inbuilt logout
    flash("You SuccessFully Logout.", 'info')
    return redirect(url_for('upload.index'))

