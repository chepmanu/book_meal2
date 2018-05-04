from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()

ma = Marshmallow()

from .models import User


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    from .api import api
    app.register_blueprint(api)
    db.init_app(app)
    ma.init_app(app)
    return app 



