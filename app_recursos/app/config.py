from redis import Redis
import os
from dotenv import load_dotenv


# Cargar variables de entorno desde el archivo .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    WTF_CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de Redis para sesiones
    SESSION_TYPE = os.getenv('SESSION_TYPE', 'redis')
    SESSION_REDIS = Redis.from_url(os.getenv('SESSION_REDIS', 'redis://localhost:6379/0'))
    SESSION_USE_SIGNER = True  # Asegura las cookies de sesión
    SESSION_PERMANENT = False  # Las sesiones no son permanentes
    SESSION_KEY_PREFIX = 'session:'  # Prefijo en Redis para las claves de sesión
    PERMANENT_SESSION_LIFETIME = int(os.getenv('SESSION_EXPIRATION', 7200))  # Expiración de la sesión (2 horas)
    
    # Actualización de cookies de sesión para evitar problemas de caching en el navegador
    SESSION_COOKIE_NAME = 'app_session'
    SESSION_COOKIE_HTTPONLY = True  # Solo se puede acceder a la cookie desde el HTTP/HTTPS
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE') == 'True'  # True para HTTPS Se recomienda tenerlo como True en producción.
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')  # Define restricciones en el uso compartido de cookies
    
    # Añadido para que las cookies expiren al cerrar el navegador
    SESSION_REFRESH_EACH_REQUEST = False  # La sesión no se renueva en cada solicitud
    SESSION_COOKIE_DURATION = None  # La cookie expira al cerrar el navegador

    # Configuración de Email
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    # Validación de configuración de correo
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        raise ValueError("Error: Faltan credenciales SMTP (MAIL_USERNAME o MAIL_PASSWORD). Verifica el archivo .env")

    if not MAIL_SERVER or not MAIL_DEFAULT_SENDER:
        raise ValueError("Error: Configuración de servidor de correo incompleta. Verifica MAIL_SERVER y MAIL_DEFAULT_SENDER en el archivo .env")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Forzar que las cookies solo se envíen a través de HTTPS en producción
