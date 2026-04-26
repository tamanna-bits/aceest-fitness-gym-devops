from flask import Flask
from app.routes import gym_routes
from dotenv import load_dotenv

import os

load_dotenv()

def create_app(config=None):
    app = Flask(__name__)

    app.config.update(
        TESTING=False,
        DEBUG=False,
        ENV=os.getenv("FLASK_ENV", "production"),
    )

    if config:
        app.config.update(config)

    app.register_blueprint(gym_routes)
    return app