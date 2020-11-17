from flask import session, request, jsonify
from user_microservice.database import db, User
from user_microservice.filter_sanitizer import sanitize_filter
from sqlalchemy import column, and_
from sqlalchemy.exc import DatabaseError, DBAPIError
from werkzeug.security import generate_password_hash


def get():
    field = None
    for kv_pair in request.args.items():
        #Grab the first one we find.
        field = kv_pair
        break
    if field:
        try:
            # usr = User.query.filter(column(kv_pair[0]) == kv_pair[1]).first()
            usr = User.query.filter(getattr(User, kv_pair[0]) == kv_pair[1]).first()
        except (DatabaseError, AttributeError) as exc:
            return str(exc), 500
        return (usr.to_dict(), 200) if usr else ({}, 404)
    else:
        return {}, 404


def create_user(*,
                email,
                firstname=None,
                lastname=None,
                password=None,
                fiscal_code=None,
                phone=None,
                dateofbirth=None,
                restaurant_id=None):
    try:
        db.session.add(
            User(email=email,
                 firstname=firstname,
                 lastname=lastname,
                 password=generate_password_hash(password) if password else "",
                 fiscal_code=fiscal_code,
                 phone=phone,
                 dateofbirth=dateofbirth,
                 restaurant_id=restaurant_id))
        db.session.commit()
    except DBAPIError as exc:
        return str(exc), 500
    user_id = User.query.filter(User.email == email).first().id
    return user_id, 201


def create():
    user_dict = request.get_json()

    if "email" in user_dict:
        return create_user(**user_dict)
    else:
        return "Email missing.", 500


def get_users():
    try:
        return list(x.to_dict() for x in User.query.all())
    except DBAPIError as exc:
        return str(exc), 500


def get_users_filtered():
    eval_str = request.get_json()
    try:
        stmt = sanitize_filter(eval_str)
        if stmt:
            return list(x.to_dict() for x in User.query.filter(eval(stmt)).all())
        else:
            return "Unsafe filter", 500
    except DBAPIError as exc:
        return str(exc), 500


def update_field(user_id, field):
    try:
        usr = User.query.filter(User.id == user_id).first()
        if hasattr(usr, field):
            setattr(usr, field, request.get_json())
            db.session.commit()
        else:
            return f"No field '{field}'", 500
    except DBAPIError as exc:
        return str(exc), 500


def get_field(user_id, field):
    try:
        usr = User.query.filter(User.id == user_id).first()
        if hasattr(usr, field):
            return getattr(usr, field)
        else:
            return f"No field '{field}'", 500
    except DBAPIError as exc:
        return str(exc), 500
