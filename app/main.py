from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os

# Create the main Flask app
app = Flask(__name__)

# Enable CORS
CORS(app)

# Serve the register_service file from root (BlueOS needs this)
@app.route('/register_service')
def serve_register_service():
    return send_from_directory('.', 'register_service')

# Serve the frontend at root (this needs to come BEFORE backend routes)
@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

# Import the backend routes and register them directly
from backend.routes import thruster, sensors, tests

# Register the backend blueprints with /api prefix
app.register_blueprint(thruster.bp, url_prefix='/api/thruster')
app.register_blueprint(sensors.bp, url_prefix='/api/sensors')
app.register_blueprint(tests.bp, url_prefix='/api/tests')

# Add a simple status endpoint
@app.route('/api/status')
def api_status():
    return {"status": "success", "message": "Flask backend running"}

@app.route('/<path:path>')
def serve_static(path):
    # Check if it's a frontend file
    if os.path.exists(os.path.join('frontend', path)):
        return send_from_directory('frontend', path)
    elif os.path.exists(os.path.join('frontend/styles', path)):
        return send_from_directory('frontend/styles', path)
    # Check if it's a static file
    elif os.path.exists(os.path.join('static', path)):
        return send_from_directory('static', path)
    else:
        return send_from_directory('frontend', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)