import os
from flask_script import Manager # class for handling a set of commands
from flask_migrate import Migrate, MigrateCommand
from app import db, create_app
from app import models

app = create_app(config_name=os.getenv('APP_SETTINGS'))
migrate = Migrate(app, db)

@app.cli.command()
def dropdb():
    db.session.commit()
    db.reflect()
    db.drop_all()


@app.cli.command()
def create_db():
    db.create_all()