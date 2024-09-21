#!/usr/bin/python3
"""
App entry point, registers the blueprints for API and Front-end routes
"""

from flask import Flask
from api.backend_routes import backend
from engine.db_storage import storage
from frontend_routes import frontend

app = Flask(__name__)

#Registering blueprints for API and front-end
app.register_blueprint(backend, url_prefix='/api')
app.register_blueprint(frontend)

# Reload the database schema (create tables)
storage.reload()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
