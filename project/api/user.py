# from .. import db
# from . import user
# from flask import request, jsonify
# from http import HTTPStatus
# from ..models import User, UserProfileSchema, Follow
# import json



import os

from flask import Blueprint, jsonify, request

from sqlalchemy import exc, and_

from project.api.models import User, UserProfileSchema, Follow
from project import db

user_blueprint = Blueprint('user', __name__)

@user_blueprint.route('/<user_id>', methods=['GET'])
def getUserModel(user_id):
    user = db.session.query(User).get(user_id)
    if not user:
        return jsonify({"data": {}})

    # viewer_id = current user id with flask login #review
    # viewer_id = 0

    # follow = db.session.query(Follow) \
    #         .filter(and_(Follow.follower_id == viewer_id,
    #                      Follow.followed_id == user_id)) \
    #         .all()
    # if not follow:
    #     user_following = False
    # else:
    #     user_following = True
    schema = UserProfileSchema()
    result, error = schema.dump(user)
    return jsonify({"data": {"user": result}})
    # return jsonify({"data": {"user": result,
    #                          "following": user_following}})

# @user.route('/profile', methods=['GET'])
# def getUserModel():
#     error = None
#     if request.method == 'GET':
#         try:
#             db.create_all()
#             json_dict = request.get_json()           # might need error handling
#             try:
#                 user = db.session.query(User).get(json_dict['user_id'])
#                 if not user:
#                     return ('There is no such user', HTTPStatus.OK)
#                 follow = db.session.query(Follow).filter(Follow.follower_id == json_dict['viewer_id']).filter(Follow.followed_id == json_dict['user_id']).all()
#                 if not follow:
#                     user_following = False
#                 else:
#                     user_following = True
#                 schema = UserProfileSchema()
#                 result, error = schema.dump(user)
#                 return jsonify({"user": result, "following": user_following})
#             except:
#                 return ('Unknown error for getUserModel', HTTPStatus.INTERNAL_SERVER_ERROR)
#         except KeyError as e:
#             error = "KeyError"
#             return (error, HTTPStatus.OK)
#     else : # Method not allow
#         return HTTPStatus.METHOD_NOT_ALLOWED
