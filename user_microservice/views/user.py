from flask import session, request, jsonify
from user_microservice.database import db, User
from user_microservice.filter_sanitizer import sanitize_filter
from sqlalchemy import column, and_, or_
from sqlalchemy.exc import DatabaseError, DBAPIError
from werkzeug.security import generate_password_hash
from datetime import datetime

# Back and forth from isoformat to datetime
def try_fromisoformat(iso):
    if type(iso) == str:
        try:
            return datetime.fromisoformat(iso)
        except ValueError:
            pass
    return None


def try_isoformat(iso):
    if type(iso) == datetime:
        try:
            return iso.isoformat()
        except ValueError:
            pass
    return None


def get():
    field = None
    for kv_pair in request.args.items():
        #Grab the first one we find.
        try:
            # usr = User.query.filter(column(kv_pair[0]) == kv_pair[1]).first()
            usr = User.query.filter(getattr(User, kv_pair[0]) == kv_pair[1]).first()
        except (DatabaseError, AttributeError) as exc:
            return str(exc), 500
        
        if usr:
            usr_dict = usr.to_dict()
            usr_dict['dateofbirth'] = try_isoformat(usr_dict['dateofbirth'])
            usr_dict['reported_positive_date'] = try_isoformat(usr_dict['reported_positive_date'])
            usr_dict['confirmed_positive_date'] = try_isoformat(usr_dict['confirmed_positive_date'])

            return usr_dict, 200 
        else:
            return {}, 404
    #If we didn't fint anything
    return {}, 404


def create_user(*,
                email,
                firstname=None,
                lastname=None,
                password=None,
                fiscal_code=None,
                phone=None,
                dateofbirth=None,
                is_admin=None,
                restaurant_id=None):
    try:
        db.session.add(
            User(email=email,
                 firstname=firstname,
                 lastname=lastname,
                 password=password,
                 fiscal_code=fiscal_code,
                 phone=phone,
                 is_admin=is_admin,
                 dateofbirth=try_fromisoformat(dateofbirth),
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
        lst = []
        for user in User.query.all():
            user_dict = user.to_dict()
            user_dict['dateofbirth'] = try_isoformat(user_dict['dateofbirth'])
            user_dict['reported_positive_date'] = try_isoformat(user_dict['reported_positive_date'])
            user_dict['confirmed_positive_date'] = try_isoformat(user_dict['confirmed_positive_date'])

            lst.append(user_dict)
        return lst
    except DBAPIError as exc:
        return str(exc), 500


def get_users_filtered():
    eval_str = request.args['filter']
    try:
        stmt = sanitize_filter(eval_str)
        if stmt:
            lst = []
            for user in User.query.filter(eval(stmt)).all():
                user_dict = user.to_dict()
                user_dict['dateofbirth'] = try_isoformat(user_dict['dateofbirth'])
                user_dict['reported_positive_date'] = try_isoformat(user_dict['reported_positive_date'])
                user_dict['confirmed_positive_date'] = try_isoformat(user_dict['confirmed_positive_date'])

                lst.append(user_dict)
            return lst
        else:
            return "Unsafe filter", 500
    except DBAPIError as exc:
        return str(exc), 500


def update_field(user_id, field):
    try:
        usr = User.query.filter(User.id == user_id).first()
        if hasattr(usr, field):
            if field in ['confirmed_positive_date', 'reported_positive_date', 'dateofbirth']:
                setattr(usr, field, datetime.fromisoformat(request.get_json()))
            else:
                setattr(usr, field, request.get_json())
            db.session.commit()
            return {}, 200
        else:
            return f"No field '{field}'", 500
    except DBAPIError as exc:
        return str(exc), 500


def get_field(user_id, field):
    try:
        usr = User.query.filter(User.id == user_id).first()
        if hasattr(usr, field):
            if field in ['confirmed_positive_date', 'reported_positive_date', 'dateofbirth']:
                return getattr(usr, field).isoformat()
            else: 
                return getattr(usr, field)
        else:
            return f"No field '{field}'", 500
    except DBAPIError as exc:
        return str(exc), 500
