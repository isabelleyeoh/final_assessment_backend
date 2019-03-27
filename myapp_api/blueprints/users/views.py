from flask import Blueprint, jsonify, make_response, request
from flask_login import login_required
from models.user import *
from werkzeug.security import generate_password_hash


users_api_blueprint = Blueprint('users_api', __name__)

@users_api_blueprint.route('/', methods=['GET'])
def index():
    users = User.select()
    # users = [(user.__dict__['__data__'] for user in users] # returns a full user object incl password!! (think of how you can exclude sensetive data from the returned JSON if you want to use this)
    users = [{"id": int(user.id), "username": user.username} for user in users]
    return jsonify(users)

@users_api_blueprint.route('/', methods=['POST'])
def create():
    # get the post data
    post_data = request.get_json()

    try:
        new_user = User(
            username=post_data['username'],
            email=post_data['email'].lower(),
            password=generate_password_hash(post_data['password'])
        )

    except:
        responseObject = {
            'status': 'failed',
            'message': ['All fields are required!']
        }

        return make_response(jsonify(responseObject)), 400

    else:

        if not new_user.save():

            responseObject = {
                'status': 'failed',
                'message': new_user.errors
            }

            return make_response(jsonify(responseObject)), 400

        else:
            # breakpoint()
            auth_token = new_user.encode_auth_token(new_user.id)

            responseObject = {
                'status': 'success',
                'message': 'Successfully created a user and signed in.',
                'auth_token': auth_token.decode(),
                'user': {"id": int(new_user.id), "username": new_user.username}
            }

            return make_response(jsonify(responseObject)), 201

@users_api_blueprint.route('/getprofile', methods=['GET'])
@login_required
def getprofile():
    user_id = User.decode_auth_token(auth_token)
    user = User.get_or_none(id=user_id)
    return jsonify(users)

@users_api_blueprint.route('/updateprofile', methods=['POST'])
@login_required
def update():

    auth_header = request.headers.get('Authorization')

    if auth_header:
        auth_token = auth_header.split(" ")[1]
        # breakpoint()

    else:
        responseObject = {
            'status': 'failed',
            'message': 'No authorization header found'
        }

        return make_response(jsonify(responseObject)), 401

    
    user_id = User.decode_auth_token(auth_token)
    user = User.get_or_none(id=user_id)
    post_data = request.get_json()
    update_username = post_data['username']
    update_password = post_data['password']

    q = User.update(username=update_username, password=update_password).where(User.id==user_id)

    if q.execute():
        responseObject = {
            'status': 'success',
            'message': 'Successfully edited.',
        }
        return make_response(jsonify(responseObject)), 201

    else:
        responseObject = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }

        return make_response(jsonify(responseObject)), 401


@users_api_blueprint.route('/delete', methods=['POST'])
@login_required
def delete():

    auth_header = request.headers.get('Authorization')

    if auth_header:
        auth_token = auth_header.split(" ")[1]
        
    else:
        responseObject = {
            'status': 'failed',
            'message': 'No authorization header found'
        }

        return make_response(jsonify(responseObject)), 401

    
    user_id = User.decode_auth_token(auth_token)
    user = User.get_or_none(id=user_id)
    q = User.delete().where(User.id==user_id)
 
    if q.execute():
        responseObject = {
            'status': 'success',
            'message': 'Successfully deleted.',
        }

        return make_response(jsonify(responseObject)), 201

    else:
        responseObject = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }

        return make_response(jsonify(responseObject)), 401

