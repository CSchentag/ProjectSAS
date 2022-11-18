from apifairy.decorators import other_responses
from flask import Blueprint, abort, jsonify
from apifairy import authenticate, body, response

from .. import db
from ..models import User
from .schemas import UserSchema, UpdateUserSchema, EmptySchema
from .auth import token_auth
from . import api_0_2

user_schema = UserSchema()
users_schema = UserSchema(many=True)
update_user_schema = UpdateUserSchema(partial=True)

@api_0_2.route('/me', methods=['GET'])
@authenticate(token_auth)
@response(user_schema)
def me():
    """Retrieve the authenticated user"""
    return token_auth.current_user()

@api_0_2.route('/me', methods=['PUT'])
@authenticate(token_auth)
@body(update_user_schema)
@response(user_schema)
def put(data):
    """Edit user information"""
    user = token_auth.current_user()
    if 'password' in data and ('old_password' not in data or
                               not user.verify_password(data['old_password'])):
        abort(400)
    user.update(data)
    db.session.commit()
    return user

@api_0_2.route('/user/<username>', methods=['GET'])
@authenticate(token_auth)
def get_user_info(username):
    user = User.query.filter_by(username=username).first()
    return jsonify(user.to_json())