from flask import session, request, jsonify
from user_microservice.database import db, User

count = 0


def get():
    global count

    db.session.add(User(email=f"user{count}@user.com"))
    db.session.commit()
    
    count = count + 1
    return str(count) + '\n', 200