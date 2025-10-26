from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

db = SQLAlchemy()
bcrypt = Bcrypt()

# Modelo de Carrera
class Carrera(db.Model):
    __tablename__ = 'carreras'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False, unique=True)
    materias = db.relationship('Materia', backref='carrera', lazy=True)
    recursos = db.relationship('Recurso', backref='carrera_rel', lazy=True, overlaps="carrera,recursos_carrera")

    def __repr__(self):
        return f'<Carrera {self.nombre}>'

# Modelo de Materia
class Materia(db.Model):
    __tablename__ = 'materias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    carrera_id = db.Column(db.Integer, db.ForeignKey('carreras.id'), nullable=False)
    recursos = db.relationship('Recurso', backref='materia_rel', lazy=True, overlaps="materia,recursos_materia")

    def __repr__(self):
        return f'<Materia {self.nombre}>'

# Modelo de usuario (Docente o Estudiante)
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    cedula = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    tipo_usuario = db.Column(db.String(50), nullable=False, index=True)  # "docente" o "estudiante"
    redes_educativas = db.Column(db.Text, nullable=True)  # Solo para docentes
    articulos_publicados = db.Column(db.Text, nullable=True)  # Solo para docentes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con carreras y materias (solo aplicable para docentes)
    carrera_id = db.Column(db.Integer, db.ForeignKey('carreras.id'), nullable=False)
    carrera = db.relationship('Carrera', backref='usuarios')  # Relación para acceder a la carrera
    materias = db.relationship('Materia', secondary='user_materia', backref='docentes')

    recursos = db.relationship('Recurso', backref='usuario', lazy=True)  # Relación para recursos del usuario

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_docente(self):
        return self.tipo_usuario == 'docente'

    @property
    def is_estudiante(self):
        return self.tipo_usuario == 'estudiante'
    
    @property
    def is_administrador(self):
        return self.tipo_usuario == 'administrador'

# Tabla intermedia entre User y Materia para reflejar las materias que imparte un docente
user_materia = db.Table('user_materia',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('materia_id', db.Integer, db.ForeignKey('materias.id'), primary_key=True)
)

class ResourceType:
    PDF = 'PDF'
    VIDEO = 'Video'
    LINK = 'Link'
    ARCHIVO = 'Archivo'
    ALL_TYPES = [PDF, VIDEO, LINK, ARCHIVO]

class CategoriaRecurso:
    BIBLIOGRAFIA = 'Bibliografia'
    VIDEOS = 'Videos'
    EXAMENES = 'Examenes'
    EJERCICIOS = 'Ejercicios'
    APLICACIONES = 'Aplicaciones'
    CHATBOT = 'Chatbot'
    ALL_CATEGORIES = [BIBLIOGRAFIA, VIDEOS, EXAMENES, EJERCICIOS, APLICACIONES, CHATBOT]

# Modelo para los recursos educativos
class Recurso(db.Model):
    __tablename__ = 'recursos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)  # Título del recurso añadido
    description = db.Column(db.Text, nullable=True)    # Descripción del recurso añadido
    file_path = db.Column(db.String(255), nullable=True)  # Para PDFs locales
    youtube_link = db.Column(db.String(255), nullable=True)  # Para videos de YouTube
    external_link = db.Column(db.String(255), nullable=True)  # Para enlaces externos (PDF)
    resource_type = db.Column(db.String(50), nullable=False)  # PDF, Video, Link o Archivo
    categoria = db.Column(db.String(50), nullable=False)  # Bibliografia, Videos, Examenes, etc.
    disponibilidad = db.Column(db.String(50), nullable=False)  # Publica o Privada
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Relación con el usuario que subió el recurso
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)  # Se cambió para no usar lambda

    # Claves foráneas
    carrera_id = db.Column(db.Integer, db.ForeignKey('carreras.id'), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id'), nullable=False)

     # Relación explícita con Carrera y Materia
    carrera = db.relationship('Carrera', backref='recursos_carrera', overlaps="carrera_rel,recursos")
    materia = db.relationship('Materia', backref='recursos_materia', overlaps="materia_rel,recursos")
    
    def __repr__(self):
        return f'<Recurso {self.title} ({self.resource_type}) - Categoria: {self.categoria}>'


# Modelo para registrar el acceso a recursos
class AccesoRecurso(db.Model):
    __tablename__ = 'acceso_recursos'
    
    id = db.Column(db.Integer, primary_key=True)
    recurso_id = db.Column(db.Integer, db.ForeignKey('recursos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null si es usuario casual
    tipo_usuario = db.Column(db.String(50), nullable=False, index=True)  # 'docente', 'estudiante', 'casual'
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    fecha_acceso = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relaciones
    recurso = db.relationship('Recurso', backref='accesos')
    usuario = db.relationship('User', backref='accesos_recursos')
    
    def __repr__(self):
        return f'<AccesoRecurso {self.recurso_id} por {self.tipo_usuario} en {self.fecha_acceso}>'


# Modelo para registrar sesiones de usuarios
class SesionUsuario(db.Model):
    __tablename__ = 'sesiones_usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null si es usuario casual
    tipo_usuario = db.Column(db.String(50), nullable=False, index=True)  # 'docente', 'estudiante', 'casual'
    session_id = db.Column(db.String(255), nullable=True, index=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    duracion_segundos = db.Column(db.Integer, nullable=True)
    
    # Relación
    usuario = db.relationship('User', backref='sesiones')
    
    def __repr__(self):
        return f'<SesionUsuario {self.tipo_usuario} - {self.fecha_inicio}>'


# Modelo para estadísticas agregadas (para optimizar consultas)
class EstadisticaDiaria(db.Model):
    __tablename__ = 'estadisticas_diarias'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False, unique=True, index=True)
    
    # Contadores de sesiones
    sesiones_total = db.Column(db.Integer, default=0)
    sesiones_docentes = db.Column(db.Integer, default=0)
    sesiones_estudiantes = db.Column(db.Integer, default=0)
    sesiones_casuales = db.Column(db.Integer, default=0)
    
    # Contadores de accesos a recursos
    accesos_recursos_total = db.Column(db.Integer, default=0)
    accesos_recursos_docentes = db.Column(db.Integer, default=0)
    accesos_recursos_estudiantes = db.Column(db.Integer, default=0)
    accesos_recursos_casuales = db.Column(db.Integer, default=0)
    
    # Usuarios únicos
    usuarios_unicos_total = db.Column(db.Integer, default=0)
    usuarios_docentes = db.Column(db.Integer, default=0)
    usuarios_estudiantes = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EstadisticaDiaria {self.fecha} - {self.sesiones_total} sesiones>'