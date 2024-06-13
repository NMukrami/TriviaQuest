from flask import Flask
import random

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.template_filter('shuffle')
    def shuffle_filter(s):
        s = list(s)
        random.shuffle(s)
        return s

    return app
