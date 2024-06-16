from flask import Flask
import random
from app.config import Config
from app.routes.main import main as main_blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(main_blueprint)

    @app.template_filter('shuffle')
    def shuffle_filter(s):
        s = list(s)
        random.shuffle(s)
        return s

    return app
