from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for frontend communication
    CORS(app)
    
    # Configure app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Register blueprints
    from .routes import thruster, sensors, tests
    app.register_blueprint(thruster.bp)
    app.register_blueprint(sensors.bp)
    app.register_blueprint(tests.bp)
    
    @app.route('/')
    def index():
        return {"message": "BR Thruster Destroyer Extension", "status": "running"}
    
    @app.route('/status')
    def status():
        return {"status": "success", "message": "Flask backend running"}
    
    return app
