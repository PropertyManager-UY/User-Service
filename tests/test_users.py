import os
import unittest
from flask import json
from models import User
from pymongo import MongoClient
from werkzeug.security import check_password_hash

class UserTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configurar la conexión a la base de datos de prueba
        cls.client = MongoClient(os.getenv('MONGO_URI'))
        cls.test_db = cls.client[os.getenv('TEST_DATABASE_NAME')]
        cls.user_model = User(cls.test_db)
        cls.users_collection = cls.user_model.users_collection

    @classmethod
    def tearDownClass(cls):
        # Borrar DB después de las pruebas
        cls.client.drop_database(os.getenv('TEST_DATABASE_NAME'))

    def setUp(self):
        # Limpiar la colección antes de cada prueba
        self.users_collection.drop()

    def test_create_user(self):
        # Prueba para verificar que se pueda crear un usuario correctamente
        result = self.user_model.create_user("test_user", "test_user@example.com", "test_password", "test_role")
        self.assertTrue(result)

        # Prueba para verificar que no se pueda crear un usuario si ya existe
        result = self.user_model.create_user("test_user", "test_user@example.com", "test_password", "test_role")
        self.assertFalse(result)

    def test_update_user(self):
        # Crear un usuario para la prueba de actualización
        self.user_model.create_user("test_user", "test_user@example.com", "test_password", "test_role")
        user = self.user_model.find_user_by_username("test_user")

        # Prueba para verificar que se pueda actualizar un usuario correctamente
        result = self.user_model.update_user(user['_id'], {"password": "new_password"})
        self.assertTrue(result)

        # Verificar que la contraseña se haya actualizado correctamente
        updated_user = self.user_model.find_user_by_id(user['_id'])
        self.assertTrue(check_password_hash(updated_user['password'], "new_password"))

        # Prueba para verificar que no se pueda actualizar un usuario que no existe
        result = self.user_model.update_user("non_existing_user_id", {"password": "new_password"})
        self.assertFalse(result)

    def test_delete_user(self):
        # Crear un usuario para la prueba de eliminación
        self.user_model.create_user("test_user", "test_user@example.com", "test_password", "test_role")
        user = self.user_model.find_user_by_username("test_user")

        # Prueba para verificar que se pueda eliminar un usuario correctamente
        result = self.user_model.delete_user(user['_id'])
        self.assertTrue(result)

        # Prueba para verificar que no se pueda eliminar un usuario que no existe
        result = self.user_model.delete_user("non_existing_user_id")
        self.assertFalse(result)

    def test_find_user(self):
        # Crear un usuario para la prueba de búsqueda
        self.user_model.create_user("test_user", "test_user@example.com", "test_password", "test_role")

        # Prueba para verificar que se pueda encontrar un usuario existente por username
        result = self.user_model.find_user_by_username("test_user")
        self.assertIsNotNone(result)

        # Prueba para verificar que se pueda encontrar un usuario existente por email
        result = self.user_model.find_user_by_email("test_user@example.com")
        self.assertIsNotNone(result)

        # Prueba para verificar que no se pueda encontrar un usuario que no existe
        result = self.user_model.find_user_by_username("non_existing_user")
        self.assertIsNone(result)

    def test_get_all_users(self):
        # Crear varios usuarios para la prueba de obtener todos los usuarios
        self.user_model.create_user("user1", "user1@example.com", "password1", "role1")
        self.user_model.create_user("user2", "user2@example.com", "password2", "role2")

        # Prueba para verificar que se puedan obtener todos los usuarios correctamente
        result = self.user_model.get_all_users()
        self.assertEqual(len(result), 2)

    def test_get_users_by_inmobiliaria(self):
        # Crear varios usuarios para la prueba de obtener usuarios por inmobiliaria
        self.user_model.create_user("user1", "user1@example.com", "password1", "role1", "inmobiliaria_id")
        self.user_model.create_user("user2", "user2@example.com", "password2", "role2", "inmobiliaria_id")

        # Prueba para verificar que se puedan obtener los usuarios de una inmobiliaria correctamente
        result = self.user_model.get_users_by_inmobiliaria("inmobiliaria_id")
        self.assertEqual(len(result), 2)

        # Prueba para verificar que no se puedan obtener los usuarios si la inmobiliaria no existe
        result = self.user_model.get_users_by_inmobiliaria("non_existing_inmobiliaria_id")
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()
