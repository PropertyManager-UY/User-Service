from flask import Flask
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from flask_session import Session
from redis import Redis
from datetime import timedelta
import os

app = Flask('auth')

# Configuraciones
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = Redis(host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')))
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = os.getenv('SESSION_KEY_PREFIX')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Configuración de seguridad de la sesión
app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookie over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Hide cookie from JavaScript
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Set 'Lax' Prevent CSRF attacks

# Inicializaciones
mongo = MongoClient(os.getenv('MONGO_URI'))
jwt = JWTManager(app)
server_session = Session(app)

# Registra Blueprint
from routes import auth_bp
from models import User

# Función para configurar la aplicación
def configure_app():
    app.user_model = User(mongo[os.getenv('DATABASE_NAME')])

# Llamamos a la función de configuración
configure_app()

app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
