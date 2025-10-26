from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FileField, SelectMultipleField, URLField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, URL
from flask_wtf.file import FileAllowed

# Formulario de login
class LoginForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Ingresar')

# Formulario de registro
class RegisterForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), EqualTo('confirm', message='Las contraseñas deben coincidir')])
    confirm = PasswordField('Confirmar Contraseña', validators=[DataRequired()])
    cedula = StringField('Cédula', validators=[DataRequired()])
    carrera = SelectField('Carrera', validators=[DataRequired()], coerce=int)
    materias = SelectMultipleField('Materias', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Registrarse')

# Formulario de reseteo de contraseña (olvidé mi contraseña)
class ForgotPasswordForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar nueva contraseña')

# Formulario para editar el perfil del usuario logueado 
class EditProfileForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    redes_educativas = TextAreaField('Redes Educativas', validators=[Optional()])
    articulos = TextAreaField('Artículos Publicados', validators=[Optional()])
    password_actual = PasswordField('Contraseña Actual', validators=[Optional()])
    nueva_password = PasswordField('Nueva Contraseña', validators=[Optional(), EqualTo('confirmar_password', message='Las contraseñas deben coincidir')])
    confirmar_password = PasswordField('Confirmar Nueva Contraseña', validators=[Optional()])
    submit = SubmitField('Guardar Cambios')

# Formulario para subir recursos (Archivos PDF)
class UploadResourceForm(FlaskForm):
    title = StringField('Título del Recurso', validators=[DataRequired()])
    description = TextAreaField('Descripción del Recurso', validators=[Optional()])
    archivo = FileField('Seleccionar archivo PDF', validators=[
        DataRequired(),
        FileAllowed(['pdf'], 'Solo se permiten archivos PDF')
    ])
    carrera = SelectField('Carrera', coerce=int, validators=[DataRequired()])
    materia = SelectField('Materia', coerce=int, validators=[DataRequired()])
    disponibilidad = SelectField('Disponibilidad', choices=[
        ('publica', 'Disponible para todo el público'),
        ('privada', 'Solo para estudiantes')
    ], validators=[DataRequired()])
    categoria = SelectField('Categoría', choices=[
        ('Bibliografia', 'Bibliografía'),
        ('Videos', 'Videos'),
        ('Examenes', 'Exámenes'),
        ('Ejercicios', 'Ejercicios'),
        ('Aplicaciones', 'Aplicaciones'),
        ('Chatbot', 'Chatbot')
    ], validators=[DataRequired()])
    submit = SubmitField('Subir Recurso')

# Formulario para subir enlaces (Links)
class UploadLinkForm(FlaskForm):
    title = StringField('Título del Enlace', validators=[DataRequired()])
    description = TextAreaField('Descripción del Enlace', validators=[Optional()])
    url = URLField('Enlace (URL)', validators=[DataRequired(), URL()])
    carrera = SelectField('Carrera', coerce=int, validators=[DataRequired()])
    materia = SelectField('Materia', coerce=int, validators=[DataRequired()])
    disponibilidad = SelectField('Disponibilidad', choices=[
        ('publica', 'Disponible para todo el público'),
        ('privada', 'Solo para estudiantes')
    ], validators=[DataRequired()])
    categoria = SelectField('Categoría', choices=[
        ('Bibliografia', 'Bibliografía'),
        ('Videos', 'Videos'),
        ('Examenes', 'Exámenes'),
        ('Ejercicios', 'Ejercicios'),
        ('Aplicaciones', 'Aplicaciones'),
        ('Chatbot', 'Chatbot')
    ], validators=[DataRequired()])
    submit = SubmitField('Subir Enlace')

# Formulario para subir videos de YouTube
class UploadVideoForm(FlaskForm):
    title = StringField('Título del Video', validators=[DataRequired()])
    description = TextAreaField('Descripción del Video', validators=[Optional()])
    youtube_url = URLField('Enlace del Video (YouTube)', validators=[DataRequired(), URL()])
    carrera = SelectField('Carrera', coerce=int, validators=[DataRequired()])
    materia = SelectField('Materia', coerce=int, validators=[DataRequired()])
    disponibilidad = SelectField('Disponibilidad', choices=[
        ('publica', 'Disponible para todo el público'),
        ('privada', 'Solo para estudiantes')
    ], validators=[DataRequired()])
    categoria = SelectField('Categoría', choices=[
        ('Bibliografia', 'Bibliografía'),
        ('Videos', 'Videos'),
        ('Examenes', 'Exámenes'),
        ('Ejercicios', 'Ejercicios'),
        ('Aplicaciones', 'Aplicaciones'),
        ('Chatbot', 'Chatbot')
    ], validators=[DataRequired()])
    submit = SubmitField('Subir Video')

# Formulario para editar recursos (Archivos PDF)
class EditResourceForm(FlaskForm):
    title = StringField('Título del Recurso', validators=[DataRequired()])
    description = TextAreaField('Descripción del Recurso', validators=[Optional()])
    archivo = FileField('Actualizar archivo PDF (opcional)', validators=[
        Optional(),
        FileAllowed(['pdf'], 'Solo se permiten archivos PDF')
    ])
    carrera = SelectField('Carrera', coerce=int, validators=[DataRequired()])
    materia = SelectField('Materia', coerce=int, validators=[DataRequired()])
    disponibilidad = SelectField('Disponibilidad', choices=[
        ('publica', 'Disponible para todo el público'),
        ('privada', 'Solo para estudiantes')
    ], validators=[DataRequired()])
    categoria = SelectField('Categoría', choices=[
        ('Bibliografia', 'Bibliografía'),
        ('Videos', 'Videos'),
        ('Examenes', 'Exámenes'),
        ('Ejercicios', 'Ejercicios'),
        ('Aplicaciones', 'Aplicaciones'),
        ('Chatbot', 'Chatbot')
    ], validators=[DataRequired()])
    submit = SubmitField('Guardar Cambios')

# Formulario para editar enlaces (Links)
class EditLinkForm(FlaskForm):
    title = StringField('Título del Enlace', validators=[DataRequired()])
    description = TextAreaField('Descripción del Enlace', validators=[Optional()])
    url = URLField('Actualizar Enlace (URL)', validators=[DataRequired(), URL()])
    carrera = SelectField('Carrera', coerce=int, validators=[DataRequired()])
    materia = SelectField('Materia', coerce=int, validators=[DataRequired()])
    disponibilidad = SelectField('Disponibilidad', choices=[
        ('publica', 'Disponible para todo el público'),
        ('privada', 'Solo para estudiantes')
    ], validators=[DataRequired()])
    categoria = SelectField('Categoría', choices=[
        ('Bibliografia', 'Bibliografía'),
        ('Videos', 'Videos'),
        ('Examenes', 'Exámenes'),
        ('Ejercicios', 'Ejercicios'),
        ('Aplicaciones', 'Aplicaciones'),
        ('Chatbot', 'Chatbot')
    ], validators=[DataRequired()])
    submit = SubmitField('Guardar Cambios')

# Formulario para editar videos de YouTube
class EditVideoForm(FlaskForm):
    title = StringField('Título del Video', validators=[DataRequired()])
    description = TextAreaField('Descripción del Video', validators=[Optional()])
    youtube_url = URLField('Actualizar Enlace del Video (YouTube)', validators=[DataRequired(), URL()])
    carrera = SelectField('Carrera', coerce=int, validators=[DataRequired()])
    materia = SelectField('Materia', coerce=int, validators=[DataRequired()])
    disponibilidad = SelectField('Disponibilidad', choices=[
        ('publica', 'Disponible para todo el público'),
        ('privada', 'Solo para estudiantes')
    ], validators=[DataRequired()])
    categoria = SelectField('Categoría', choices=[
        ('Bibliografia', 'Bibliografía'),
        ('Videos', 'Videos'),
        ('Examenes', 'Exámenes'),
        ('Ejercicios', 'Ejercicios'),
        ('Aplicaciones', 'Aplicaciones'),
        ('Chatbot', 'Chatbot')
    ], validators=[DataRequired()])
    submit = SubmitField('Guardar Cambios')
