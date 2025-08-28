from flask import Flask, send_from_directory
from flask_cors import CORS
import os

# Import the backend app factory
from backend import create_app

# Create the Flask app
app = create_app()

# Serve the frontend
@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join('frontend', path)):
        return send_from_directory('frontend', path)
    elif os.path.exists(os.path.join('frontend/styles', path)):
        return send_from_directory('frontend/styles', path)
    else:
        return send_from_directory('frontend', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
