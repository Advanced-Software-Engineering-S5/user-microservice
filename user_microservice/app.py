import connexion
from flask_jwt_extended import JWTManager, create_access_token
from user_microservice.database import db, User
import os

jwt = JWTManager()


def create_app(dbfile="userdb.db"):
    app = connexion.FlaskApp(__name__)
    app.add_api("user.yml")

    #Grab the Flask object from the connexion app
    flask_app = app.app

    flask_app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{dbfile}"
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    flask_app.config["JWT_SECRET_KEY"] = "secret_key_bella_e_nascosta"
    flask_app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    flask_app.config['JWT_ACCESS_COOKIE_NAME'] = 'gooutsafe_jwt_token'
    flask_app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    flask_app.config['JWT_CSRF_IN_COOKIES'] = True
    flask_app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

    # celery config
    flask_app.config['CELERY_BROKER_URL'] = f"redis://{os.environ.get('GOS_REDIS')}/{os.environ.get('CELERY_DB_NUM')}"
    flask_app.config[
        'CELERY_RESULT_BACKEND'] = f"redis://{os.environ.get('GOS_REDIS')}/{os.environ.get('CELERY_DB_NUM')}"

    # Bind JWT manager
    jwt.init_app(flask_app)

    # Binds the database to the Flask app
    db.init_app(flask_app)
    # Creates the database file and builds the tables
    db.create_all(app=flask_app)

    with flask_app.app_context():
        db.session.add(
            User(email="health@authority.com",
                 firstname="admin",
                 lastname="admin",
                 password='admin',
                 fiscal_code='culo',
                 phone='1111111111',
                 is_admin=True))
        db.session.commit()

    return flask_app


if __name__ == "__main__":  #pragma: no cover
    import sys
    app = create_app(sys.argv[1])
    app.run()