from flask import Flask

def create_app():
    app = Flask(__name__)

    from .routes import main  # Import the blueprint from routes.py
    app.register_blueprint(main)  # Register the blueprint

    return app
