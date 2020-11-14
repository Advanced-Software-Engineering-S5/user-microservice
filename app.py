from flask import Flask
from user_microservice.views import views
from user_microservice.database import db


def create_app(dbfile="userdb.db"):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{dbfile}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    for bp in views:
        app.register_blueprint(bp)
        bp.app = app

    # Binds the database to the Flask app
    db.init_app(app)
    # Creates the database file and builds the tables
    db.create_all(app=app)

    return app