from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    from app.routes import auth, dashboard, products, operations, warehouses, profile
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(operations.bp)
    app.register_blueprint(warehouses.bp)
    app.register_blueprint(profile.bp)
    
    with app.app_context():
        db.create_all()
    
    return app
