from flask_jwt_extended import create_access_token
from flask import session, request, jsonify
from user_microservice.database import db, User
from sqlalchemy.exc import DatabaseError, DBAPIError
from werkzeug.security import check_password_hash, generate_password_hash

def auth():
    data = request.get_json()
    try:
        usr = User.query.filter(User.email == data['email']).first()
        if usr and check_password_hash(usr.password, data['password']):
            token = create_access_token(identity=usr.id)
            return str(token), 200
        else:
            return "Authorization failed", 401
    except DBAPIError as exc:
        return str(exc), 500
