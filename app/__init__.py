from flask import Flask
from .routes import gym_routes

def create_app():
    app = Flask(__name__)
    app.register_blueprint(gym_routes)
    return app