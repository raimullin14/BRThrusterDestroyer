from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os

# Import the backend app factory
from backend import create_app

# Create the Flask app
app = create_app()

# Serve the register_service file at the root level (BlueOS needs this)
@app.route('/register_service')
def serve_register_service():
    return send_from_directory('static', 'register_service')

# Serve the register_service as JSON (alternative format)
@app.route('/register_service.json')
def serve_register_service_json():
    return jsonify({
        "name": "BR Thruster Destroyer",
        "description": "Thruster Testing and Data Logging Extension for BlueOS",
        "icon": "mdi-propeller",
        "company": "Blue Robotics",
        "version": "0.0.1",
        "webpage": "https://github.com/raimullin14/BRThrusterDestroyer",
        "api": "/docs",
        "route": "/"
    })

# Serve the frontend
@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

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
    port = int(os.environ.get('PORT', 8001))
    app.run(host='0.0.0.0', port=port, debug=True)