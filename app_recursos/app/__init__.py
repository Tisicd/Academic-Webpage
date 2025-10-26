from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from .models import db, User, Carrera, Materia
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

# Inicializar extensiones
session = Session()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()
mail = Mail()  # Flask-Mail

app = None  # Definir app a nivel global para importarla en otros módulos

def create_app():
    global app  # Permitir que la app sea accesible fuera de esta función

    # Cargar las variables de entorno desde el archivo .env
    load_dotenv()

    # Inicializar la aplicación Flask
    app = Flask(__name__)

    # Inicializar CSRF Protection después de crear 'app'
    csrf.init_app(app)
    
    # Verificar si es desarrollo o producción desde la variable de entorno FLASK_ENV
    if os.getenv('FLASK_ENV') == 'development':
        app.config.from_object('app_recursos.app.config.DevelopmentConfig')
    else:
        app.config.from_object('app_recursos.app.config.ProductionConfig')

    # Inicializar extensiones con la app
    db.init_app(app)
    session.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)  # Inicializar Flask-Mail con la app
    login_manager.init_app(app)
    
    # Configuraciones de Login Manager
    login_manager.login_view = 'app_bp.login'  
    login_manager.login_message = "Por favor, inicie sesión para acceder a esta página."

    # Registrar blueprints (rutas)
    from .routes import app_bp
    app.register_blueprint(app_bp)

    # Definir la carpeta de subidas desde una variable de entorno
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', definir_carpeta_subidas())

    # Cargar el usuario por ID
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registrar middleware para tracking de sesiones casuales
    @app.before_request
    def track_casual_user():
        """Middleware para registrar sesiones de usuarios casuales"""
        from flask_login import current_user
        from flask import session
        import uuid
        
        # Solo rastrear si no es una petición a archivos estáticos o API
        if request.endpoint and not request.endpoint.startswith('static'):
            # Si el usuario no está autenticado y no tiene session_id
            if not current_user.is_authenticated and 'session_id' not in session:
                session_id = str(uuid.uuid4())
                session['session_id'] = session_id
                # Registrar sesión casual (comentado temporalmente para debugging)
                # try:
                #     from .services import AnalyticsService
                #     AnalyticsService.registrar_inicio_sesion(user_id=None, session_id=session_id)
                # except Exception as e:
                #     print(f"Error registrando sesión casual: {e}")
    
    # Asegurarse de que las tablas se creen en la base de datos y crear datos de prueba si es necesario
    with app.app_context():
        inicializar_base_de_datos()

    return app

def definir_carpeta_subidas():
    """Define y asegura la existencia de la carpeta para subir archivos."""
    upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    return upload_folder

def guardar_archivo_categoria(file, categoria, filename):
    """Guarda el archivo en una subcarpeta específica según la categoría."""
    categoria_folder = os.path.join(definir_carpeta_subidas(), categoria.lower())
    if not os.path.exists(categoria_folder):
        os.makedirs(categoria_folder)
    file_path = os.path.join(categoria_folder, filename)
    file.save(file_path)
    return file_path

def inicializar_base_de_datos():
    """Crea las tablas en la base de datos y agrega datos de prueba si es necesario."""
    try:
        db.create_all()
        print("Tablas creadas o existentes verificadas con éxito.")

        # Agregar carreras y materias de prueba
        if Carrera.query.count() == 0:
            agregar_carreras_materias_prueba()

        # Agregar usuarios de prueba
        if User.query.count() == 0:
            agregar_usuarios_prueba()

    except Exception as e:
        print(f"Error durante la creación de la base de datos: {str(e)}")

def agregar_carreras_materias_prueba():
    """Agrega carreras y materias de prueba a la base de datos."""
    print("Agregando carreras y materias de prueba...")

    # Crear carreras
    carreras = [
        Carrera(nombre="Economía"),
        Carrera(nombre="Finanzas"),
        Carrera(nombre="Estadística")
    ]

    db.session.add_all(carreras)
    db.session.commit()

    # Crear materias para cada carrera
    materias = [
        Materia(nombre="Álgebra Lineal", carrera_id=carreras[0].id),
        Materia(nombre="Matemática Básica", carrera_id=carreras[0].id),
        Materia(nombre="Matemática I", carrera_id=carreras[0].id),
        Materia(nombre="Matemática II", carrera_id=carreras[0].id),
        Materia(nombre="Cálculo Diferencial", carrera_id=carreras[1].id),
        Materia(nombre="Cálculo Integral", carrera_id=carreras[1].id),
        Materia(nombre="Cálculo I", carrera_id=carreras[2].id),
        Materia(nombre="Cálculo II", carrera_id=carreras[2].id),
        Materia(nombre="Cálculo III", carrera_id=carreras[2].id),
        Materia(nombre="Ecuaciones Diferenciales", carrera_id=carreras[2].id)
    ]

    db.session.add_all(materias)
    db.session.commit()
    print("Carreras y materias agregadas correctamente.")

def agregar_usuarios_prueba():
    """Agrega usuarios de prueba a la base de datos."""
    print("Agregando usuarios de prueba...")

    # Obtener carreras de la base de datos
    carrera_economia = Carrera.query.filter_by(nombre='Economía').first()
    carrera_finanzas = Carrera.query.filter_by(nombre='Finanzas').first()

    # Obtener materias específicas
    materia_algebra_lineal = Materia.query.filter_by(nombre='Álgebra Lineal').first()
    materia_calculo_diferencial = Materia.query.filter_by(nombre='Cálculo Diferencial').first()

    # Crear usuarios de prueba
    user1 = User(
        username='docente1',
        email='docente1@example.com',
        password_hash=bcrypt.generate_password_hash('password123').decode('utf-8'),
        cedula='1234567890',
        nombre='Juan',
        apellido='Pérez',
        carrera_id=carrera_economia.id,
        tipo_usuario='docente',
        redes_educativas='https://linkedin.com/in/juanperez, https://youtube.com/juanperez',
        articulos_publicados='https://researchgate.net/juanperez1'
    )
    user1.materias.append(materia_algebra_lineal)

    user2 = User(
        username='docente2',
        email='docente2@example.com',
        password_hash=bcrypt.generate_password_hash('password456').decode('utf-8'),
        cedula='0987654321',
        nombre='María',
        apellido='Gómez',
        carrera_id=carrera_finanzas.id,
        tipo_usuario='docente',
        redes_educativas='https://linkedin.com/in/mariagomez, https://youtube.com/mariagomez',
        articulos_publicados='https://researchgate.net/mariagomez1'
    )
    user2.materias.append(materia_calculo_diferencial)

    user3 = User(
        username='estudiante1',
        email='estudiante1@example.com',
        password_hash=bcrypt.generate_password_hash('password789').decode('utf-8'),
        cedula='1122334455',
        nombre='Carlos',
        apellido='Sánchez',
        carrera_id=carrera_economia.id,
        tipo_usuario='estudiante'
    )

    db.session.add_all([user1, user2, user3])
    db.session.commit()
    print("Usuarios agregados correctamente.")
