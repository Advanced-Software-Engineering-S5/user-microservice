from flask import Blueprint, session, request, jsonify

user_bp = Blueprint("user", __name__)

count = 0

@user_bp.route("/get")
def get():
    global count

    count = count + 1
    return str(count) + '\n', 200