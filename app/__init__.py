from flask import Flask,render_template,request,redirect,url_for,session,Response,Blueprint
from werkzeug.security import generate_password_hash,check_password_hash
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db=SQLAlchemy()
loginManager = LoginManager()

def create_app():
    app=Flask(__name__)
    app.config["SECRET_KEY"]="CHECKIT"

    #creating a upload folder for storing the uploaded files
    app.config["UPLOAD_FOLDER"]="app/static/uploads"
    
 
    #Uploading a File to The Server
    basedir=os.path.abspath(os.path.dirname(__file__))
    UPLOAD_PATH=os.path.join(basedir,"static","uploads")
    #Create the uploads directory if it doesn't exist
    os.makedirs(UPLOAD_PATH,exist_ok=True)

    #DataBase Configuration
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///skinbuzz.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    db.init_app(app)

    #Login Manager Configuration
    loginManager.init_app(app)
    loginManager.login_view = 'auth.login'  # Redirect to login page if not authenticated
    loginManager.login_message_category = 'info'  # Flash message category for login required
    
    from app.models import User
    @loginManager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    
    from app.routes import register_routes
    register_routes(app)
    
    return app



    