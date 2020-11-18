import connexion
from flask_jwt_extended import JWTManager, create_access_token
from user_microservice.database import db

jwt = JWTManager()

def create_app(dbfile="userdb.db"):
    app = connexion.FlaskApp(__name__)
    app.add_api("user.yml")

    #Grab the Flask object from the connexion app
    flask_app = app.app

    flask_app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{dbfile}"
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    flask_app.config["JWT_SECRET_KEY"] = "secret_key_bella_e_nascosta"

    # Bind JWT manager
    jwt.init_app(flask_app)

    # Binds the database to the Flask app
    db.init_app(flask_app)
    # Creates the database file and builds the tables
    db.create_all(app=flask_app)

    return flask_app


if __name__ == "__main__":
    import sys
    app = create_app(sys.argv[1])
    app.run()