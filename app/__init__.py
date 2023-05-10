
from flask import Flask, current_app
# from .dbcon import AsyncDatabaseSession, Base
from .api.register.main import register_bp
from .api.auth.main import auth_bp, refresh_token_bp
from .api.pins.main import pins_bp
# from .api.pins.main import pins_bp1, pins_bp
from flask_jwt_extended import JWTManager
from flask_cors import CORS



def create_app():
    app = Flask(__name__)
    #Enable CORS Support
    CORS(app)
    # register blueprints
    app.register_blueprint(register_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(refresh_token_bp)
    # app.register_blueprint(pins_bp1)
    app.register_blueprint(pins_bp)

    # initialize jwt manager
    app.config['JWT_SECRET_KEY'] = 'super-secret'
    jwt = JWTManager(app)
    return app
