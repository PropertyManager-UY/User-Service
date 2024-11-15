import os
import uuid
from werkzeug.security import generate_password_hash

class User:
    def __init__(self, db):
        self.db = db
        self.users_collection = self.db[os.getenv('AUTH_COLLECTION')]

    def create_user(self, username, email, password, role, id_inmobiliaria=None):
        if self.users_collection.find_one({"$or": [{"username": username}, {"email": email}]}):
            return False
        hashed_password = generate_password_hash(password)
        user_id = str(uuid.uuid4())
        user = {
            "_id": user_id,
            "username": username,
            "email": email,
            "password": hashed_password,
            "role": role,
            "id_inmobiliaria": id_inmobiliaria
        }
        self.users_collection.insert_one(user)
        return True

    def update_user(self, user_id, updated_fields):
        user = self.find_user_by_id(user_id)
        if not user:
            return False

        update_data = {}
        if 'password' in updated_fields:
            update_data['password'] = generate_password_hash(updated_fields['password'])
        if 'role' in updated_fields:
            update_data['role'] = updated_fields['role']
        if 'id_inmobiliaria' in updated_fields:
            update_data['id_inmobiliaria'] = updated_fields['id_inmobiliaria']
        if 'email' in updated_fields:
            if self.users_collection.find_one({"email": updated_fields['email']}):
                return False  # Email already exists
            update_data['email'] = updated_fields['email']
        if 'username' in updated_fields:
            if self.users_collection.find_one({"username": updated_fields['username']}):
                return False  # User Name already exists
            update_data['username'] = updated_fields['username']
        
        result = self.users_collection.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    def delete_user(self, user_id):
        result = self.users_collection.delete_one({"_id": user_id})
        return result.deleted_count > 0

    def find_user_by_username(self, username):
        return self.users_collection.find_one({"username": username})

    def find_user_by_email(self, email):
        return self.users_collection.find_one({"email": email})

    def find_user_by_id(self, user_id):
        return self.users_collection.find_one({"_id": user_id})

    def get_all_users(self):
        return list(self.users_collection.find())

    def get_users_by_inmobiliaria(self, id_inmobiliaria):
        return list(self.users_collection.find({"id_inmobiliaria": id_inmobiliaria}))
