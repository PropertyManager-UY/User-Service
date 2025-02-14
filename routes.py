from flask import Blueprint, current_app, request, jsonify, session
from flask_jwt_extended import create_access_token, decode_token
from werkzeug.security import check_password_hash
from functools import wraps
from jwt import ExpiredSignatureError, InvalidTokenError
import re

auth_bp = Blueprint('auth', __name__)

def session_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get('access_token')
        if not token:
            return jsonify(message="Permission denied"), 403
        try:
            decoded_token = decode_token(token)
            current_user = decoded_token['sub']
            kwargs['current_user'] = current_user
        except ExpiredSignatureError:
            return jsonify(message="Token has expired"), 401
        except InvalidTokenError:
            return jsonify(message="Invalid token"), 401
        return f(*args, **kwargs)
    return decorated_function

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

@auth_bp.route('/session_status', methods=['GET'])
@session_required
def session_status(current_user):
    return jsonify(message=f"This is the current user: {current_user}", logged_in=True), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    user_model = current_app.user_model
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not is_valid_email(email):
        return jsonify(message="Invalid email format"), 400

    if user_model.create_user(username, email, password, role):
        return jsonify(message="User created successfully"), 201
    else:
        return jsonify(message="User or email already exists"), 409

@auth_bp.route('/profile', methods=['GET'])
@auth_bp.route('/profile/<user_id>', methods=['GET'])
@session_required
def profile(current_user, user_id=None):
    user_model = current_app.user_model

    if user_id is None:
        user_id = current_user['id']

    user_data = user_model.find_user_by_id(user_id)

    if user_data:
        filtered_data = {
            "username": user_data["username"],
            "email": user_data["email"],
            "role": user_data["role"]
        }
        return jsonify(user_data=filtered_data), 200
    else:
        return jsonify(message="User not found"), 404

@auth_bp.route('/register_member', methods=['POST'])
@auth_bp.route('/register_member/<id_inmobiliaria>', methods=['POST'])
@session_required
def register_member(current_user, id_inmobiliaria=None):
    user_model = current_app.user_model

    if id_inmobiliaria is None:
        id_inmobiliaria = current_user['id_inmobiliaria']

    if current_user['role'] not in ['admin', 'owner']:
        return jsonify(message="Permission denied"), 403
    elif current_user['role'] == 'owner' and id_inmobiliaria != current_user['id_inmobiliaria']:
        id_inmobiliaria = current_user['id_inmobiliaria']

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = 'agente'

    if not is_valid_email(email):
        return jsonify(message="Invalid email format"), 400

    if user_model.create_user(username, email, password, role, id_inmobiliaria):
        return jsonify(message="Member registered successfully"), 201
    else:
        return jsonify(message="User or email already exists"), 409

@auth_bp.route('/login', methods=['POST'])
def login():
    user_model = current_app.user_model
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = user_model.find_user_by_email(email)
    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity={'id': user['_id'], 'username': user['username'], 'role': user['role'], 'id_inmobiliaria': user['id_inmobiliaria']})
        session['access_token'] = access_token
        decoded_token=decode_token(access_token)
        current_user=decoded_token['sub']
        return jsonify(message="Logged in successfully", access_token=access_token, token_content=decoded_token, user=current_user), 200
    else:
        return jsonify(message="Invalid credentials"), 401

@auth_bp.route('/logout', methods=['POST'])
@session_required
def logout(current_user):
    session_id = request.cookies.get('session')
    print(f"Session ID {session_id} has been logged out")
    session.clear()
    return jsonify(message="Logged out successfully"), 200

@auth_bp.route('/delete', methods=['DELETE'])
@auth_bp.route('/delete/<user_id>', methods=['DELETE'])
@session_required
def delete_user(current_user, user_id=None):
    user_model = current_app.user_model
    
    if user_id is None:
        user_id = current_user['id']
    
    # Check if the user is admin or the owner of the account
    if current_user['role'] == 'admin' or current_user['id'] == user_id:
        if user_model.delete_user(user_id):
            return jsonify(message="User deleted successfully"), 200
        else:
            return jsonify(message="User not found"), 404
    else:
        return jsonify(message="Permission denied"), 403

@auth_bp.route('/update', methods=['PUT'])
@auth_bp.route('/update/<user_id>', methods=['PUT'])
@session_required
def update_user(current_user, user_id=None):
    user_model = current_app.user_model
    data = request.get_json()

    if user_id is None:
        user_id = current_user['id']

    if current_user['role'] != 'admin' and current_user['id'] != user_id:
        return jsonify(message="Permission denied"), 403

    if 'id_inmobiliaria' in data and current_user['role'] != 'admin':
        return jsonify(message="Only admin can update id_inmobiliaria"), 403

    update_data = {key: value for key, value in data.items() if key != 'role' or current_user['role'] == 'admin'}

    if user_model.update_user(user_id, update_data):
        return jsonify(message="User updated successfully"), 200
    else:
        return jsonify(message="Error updating user"), 500

@auth_bp.route('/users', methods=['GET'])
@session_required
def get_all_users(current_user):
    user_model = current_app.user_model
    if current_user['role'] != 'admin':
        return jsonify(message="Permission denied"), 403
    all_users = user_model.get_all_users()
    return jsonify(users=all_users), 200

@auth_bp.route('/users/inmobiliaria', methods=['GET'])
@auth_bp.route('/users/inmobiliaria/<id_inmobiliaria>', methods=['GET'])
@session_required
def get_users_by_inmobiliaria(current_user, id_inmobiliaria=None):
    user_model = current_app.user_model

    if id_inmobiliaria is None:
        if current_user['id_inmobiliaria'] is None:
            return jsonify(message="Debes pertenecer a una inmobiliaria para esta acción"), 403
        id_inmobiliaria = current_user['id_inmobiliaria']

    if current_user['role'] == 'admin':
        found_users = user_model.get_users_by_inmobiliaria(id_inmobiliaria)
        return jsonify(users=found_users), 200
    elif current_user['role'] in ['owner', 'agente']:
        if current_user['id_inmobiliaria'] != id_inmobiliaria:
            return jsonify(message="Permission denied"), 403
        found_users = user_model.get_users_by_inmobiliaria(id_inmobiliaria)
        return jsonify(users=found_users), 200
    else:
        return jsonify(message="Permission denied"), 403
