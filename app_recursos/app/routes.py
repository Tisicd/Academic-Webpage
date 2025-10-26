from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, make_response, session, current_app, send_file
from flask_login import current_user, login_user, logout_user, login_required
from .forms import LoginForm, RegisterForm, ForgotPasswordForm, EditProfileForm, UploadLinkForm, UploadResourceForm, UploadVideoForm, EditResourceForm, EditLinkForm, EditVideoForm
from .models import User, Carrera, Materia, Recurso
from .utils import enviar_correo_confirmacion, enviar_correo_cambio_password
from .services import AnalyticsService, RecursoService, ValidacionService
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db, bcrypt  # Importa bcrypt
from functools import wraps
from redis import Redis
import uuid
import string
import secrets
import os
import re



# Crear un blueprint para las rutas
app_bp = Blueprint('app_bp', __name__)

# Configurar la conexión a Redis
redis_client = Redis.from_url(os.getenv('SESSION_REDIS', 'redis://localhost:6379/0'))

# Función para evitar caché
def no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Ruta para el home
@app_bp.route('/')
def index():
    return render_template('index.html')

# Decorador para evitar caché
from functools import wraps

def no_cache_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return decorated_function

# Ruta para login
@app_bp.route('/login', methods=['GET', 'POST'])
@no_cache_decorator
def login():
    if current_user.is_authenticated:
        # Si el usuario ya está autenticado, redirigir a la página principal
        return redirect(url_for('app_bp.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            # Generar un identificador único para la sesión
            session_id = str(uuid.uuid4())

            # Verificar si el usuario ya tiene una sesión activa
            active_session = redis_client.get(f"user_session:{user.id}")
            if active_session:
                # Invalidar la sesión anterior si el usuario intenta iniciar en un nuevo dispositivo
                redis_client.delete(f"session:{active_session.decode('utf-8')}")
                redis_client.delete(f"user_session:{user.id}")

            # Guardar la nueva sesión en Redis
            redis_client.set(f"user_session:{user.id}", session_id)
            redis_client.set(f"session:{session_id}", user.id, ex=os.getenv('SESSION_EXPIRATION', 7200))

            # Guardar el ID de sesión en la sesión de Flask
            session['session_id'] = session_id

            # Obtener el valor del checkbox de "Recordarme"
            remember = 'remember' in request.form

            # Iniciar sesión del usuario
            login_user(user, remember=remember)

            # Configuración para que la cookie expire al cerrar el navegador
            session.permanent = False
            
            # Registrar inicio de sesión en analytics (con manejo de errores)
            try:
                AnalyticsService.registrar_inicio_sesion(user_id=user.id, session_id=session_id)
            except Exception as e:
                print(f"Error en analytics (no crítico): {e}")
                # Continuar con el login aunque falle analytics

            # Determinar página de redirección según tipo de usuario
            next_page = request.args.get('next')
            if next_page:
                # Si hay una página específica solicitada, redirigir ahí
                redirect_url = next_page
            elif user.is_administrador:
                # Administradores van directo al panel de administración
                flash(f'¡Bienvenido Administrador {user.nombre}! Has sido redirigido al panel de administración.', 'success')
                redirect_url = url_for('app_bp.admin_dashboard')
            else:
                # Otros usuarios van al inicio
                redirect_url = url_for('app_bp.index')
            
            return redirect(redirect_url)
        else:
            flash('Usuario o contraseña incorrectos. Por favor, regístrate si no tienes una cuenta.', 'danger')

    # Renderizar el formulario con cabeceras para evitar caché
    response = make_response(render_template('login.html', form=form))
    return response

# Ruta para obtener materias por carrera
@app_bp.route('/materias_por_carrera/<int:carrera_id>', methods=['GET'])
def materias_por_carrera(carrera_id):
    materias = Materia.query.filter_by(carrera_id=carrera_id).all()
    materias_list = [{'id': materia.id, 'nombre': materia.nombre} for materia in materias]
    return jsonify(materias_list)


# Ruta para registro
@app_bp.route('/registro', methods=['GET', 'POST'])
@no_cache_decorator
def registro():
    if current_user.is_authenticated:
        # Si el usuario ya está autenticado, redirigir a la página principal
        return redirect(url_for('app_bp.index'))

    form = RegisterForm()
    form.carrera.choices = [(carrera.id, carrera.nombre) for carrera in Carrera.query.all()]  # Obtener las carreras de la base de datos
    form.materias.choices = [(materia.id, materia.nombre) for materia in Materia.query.all()]  # Inicializar materias vacías

    if request.method == 'POST' and form.validate_on_submit():
        # Verificar si se ha seleccionado una carrera
        if not form.carrera.data:
            flash('Seleccione una carrera para continuar.', 'danger')
            response = make_response(render_template('registro.html', form=form))
            return response

        # Llenar las materias en función de la carrera seleccionada
        materias_ids = request.form.getlist('materias')
        
        # Validar que el correo tenga el dominio correcto
        if not form.email.data.endswith('@uce.edu.ec'):
            flash('El registro de usuarios es únicamente para estudiantes de la Universidad Central del Ecuador de la Facultad de Ciencias Económicas.', 'danger')
            response = make_response(render_template('registro.html', form=form))
            return response

        # Verificar si la cédula ya está registrada
        if User.query.filter_by(cedula=form.cedula.data).first():
            flash('La cédula ya está registrada. Por favor, inicie sesión o use otra cédula.', 'danger')
            response = make_response(render_template('registro.html', form=form))
            return response

        # Validar la cédula ecuatoriana
        if not ValidacionService.validar_cedula_ecuatoriana(form.cedula.data):
            flash('La cédula ingresada no es válida. Por favor, ingrese una cédula ecuatoriana correcta.', 'danger')
            response = make_response(render_template('registro.html', form=form))
            return response

        # Crear un nombre de usuario a partir del correo
        base_username = form.email.data.split('@')[0]
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1

        # Crear el nuevo usuario con tipo de usuario "estudiante"
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        nuevo_usuario = User(
            username=username,
            email=form.email.data,
            password_hash=hashed_password,
            cedula=form.cedula.data,
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            tipo_usuario='estudiante',
            carrera_id=form.carrera.data
        )

        # Añadir las materias seleccionadas al estudiante
        materias = Materia.query.filter(Materia.id.in_(materias_ids)).all()
        nuevo_usuario.materias.extend(materias)

        db.session.add(nuevo_usuario)
        db.session.commit()

        # Enviar correo de confirmación
        enviar_correo_confirmacion(form.email.data, form.nombre.data)

        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('app_bp.login'))
    
    

    response = make_response(render_template('registro.html', form=form))
    return response


# Ruta para forgot password
@app_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generar una nueva contraseña temporal
            characters = string.ascii_letters + string.digits
            temp_password = ''.join(secrets.choice(characters) for _ in range(10))

            # Hashear la nueva contraseña temporal
            hashed_password = bcrypt.generate_password_hash(temp_password).decode('utf-8')
            user.password_hash = hashed_password

            # Guardar la nueva contraseña en la base de datos
            db.session.commit()

            # Enviar correo
            enviar_correo_cambio_password(user.email, user.nombre, temp_password)
            
            flash('Se ha enviado un correo con tu nueva contraseña temporal.', 'info')
        else:
            flash('No se encontró ningún usuario con el correo proporcionado.', 'danger')

    return render_template('forgotpass.html', form=form)
   
# Ruta para logout
@app_bp.route('/logout')
@login_required
def logout():
    # Obtener el ID de sesión de Flask
    session_id = session.get('session_id')

    if session_id:
        # Registrar fin de sesión en analytics
        AnalyticsService.registrar_fin_sesion(session_id)
        
        # Eliminar la sesión de Redis
        redis_client.delete(f"session:{session_id}")
        redis_client.delete(f"user_session:{current_user.id}")

    # Cerrar la sesión del usuario
    logout_user()

    # Limpiar la sesión de Flask
    session.clear()

    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('app_bp.index'))

# Ruta para editar el perfil del usuario logueado
@app_bp.route('/editar-perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = EditProfileForm(obj=current_user)  # Pre-cargar datos actuales del usuario

    if form.validate_on_submit():
        # Actualizar los datos del perfil del usuario logueado
        current_user.nombre = form.nombre.data
        current_user.apellido = form.apellido.data
        current_user.redes_educativas = form.redes_educativas.data
        current_user.articulos_publicados = form.articulos.data

        # Verificar si el usuario desea cambiar su contraseña
        if form.nueva_password.data:
            # Validar la contraseña actual
            if not current_user.check_password(form.password_actual.data):
                flash('La contraseña actual es incorrecta.', 'danger')
                return redirect(url_for('app_bp.editar_perfil'))

            # Actualizar la contraseña
            hashed_password = bcrypt.generate_password_hash(form.nueva_password.data).decode('utf-8')
            current_user.password_hash = hashed_password

        # Guardar los cambios en la base de datos
        try:
            db.session.commit()
            flash('Perfil actualizado correctamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el perfil: {str(e)}', 'danger')

    # Renderizar la plantilla con el formulario y los datos del perfil del usuario actual
    return render_template('editar_perfil.html', form=form, perfil=current_user)


# Ruta para eliminar un recurso (se aplica a cualquier tipo de recurso)
@app_bp.route('/eliminar-recurso/<int:recurso_id>', methods=['POST'])
@login_required
def eliminar_recurso(recurso_id):
    recurso = Recurso.query.get_or_404(recurso_id)

    # Verificar si el recurso fue subido por el usuario logueado
    if recurso.uploaded_by != current_user.id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'No tienes permiso para eliminar este recurso.'}), 403
        else:
            flash('No tienes permiso para eliminar este recurso.', 'danger')
            return redirect(url_for('app_bp.gestionar_recursos'))

    # Eliminar el recurso
    db.session.delete(recurso)
    db.session.commit()

    # Verificar si la solicitud es AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'message': 'Recurso eliminado correctamente.'}), 200
    else:
        # Si la solicitud no es AJAX, redireccionar al usuario
        flash('Recurso eliminado correctamente.', 'success')
        return redirect(url_for('app_bp.gestionar_recursos'))

# Ruta para obtener los detalles de un recurso (para editar)
@app_bp.route('/recurso/<int:recurso_id>', methods=['GET'])
@login_required
def obtener_recurso(recurso_id):
    recurso = Recurso.query.get_or_404(recurso_id)

    # Verificar si el recurso fue subido por el usuario logueado
    if recurso.uploaded_by != current_user.id:
        return jsonify({'error': 'No tienes permiso para ver este recurso.'}), 403

    return jsonify({
        'title': recurso.title,
        'description': recurso.description,
        'youtube_link': recurso.youtube_link,
        'materia_id': recurso.materia_id
    }), 200

# Ruta para editar los recursos
@app_bp.route('/editar-recurso/<int:recurso_id>', methods=['POST'])
@login_required
def editar_recurso(recurso_id):
    recurso = Recurso.query.get_or_404(recurso_id)

    # Verificar si el recurso fue subido por el usuario logueado
    if recurso.uploaded_by != current_user.id:
        return jsonify({'error': 'No tienes permiso para editar este recurso.'}), 403

    # Crear el formulario para edición, seleccionando el formulario según el tipo de recurso
    if recurso.resource_type == 'Link':
        form = EditLinkForm(obj=recurso)
    elif recurso.resource_type == 'Archivo':
        form = EditResourceForm(obj=recurso)
    elif recurso.resource_type == 'Video':
        form = EditVideoForm(obj=recurso)
    else:
        flash('Tipo de recurso desconocido.', 'danger')
        return redirect(url_for('app_bp.gestionar_recursos'))

    # Ajustar las opciones de carrera y materia en el formulario
    form.carrera.choices = [(carrera.id, carrera.nombre) for carrera in Carrera.query.all()]
    form.materia.choices = [(materia.id, materia.nombre) for materia in Materia.query.all()]

    # Verificar si el formulario es válido al enviarse mediante POST
    if form.validate_on_submit():
        # Actualizar el recurso con los datos del formulario
        recurso.title = form.title.data
        recurso.description = form.description.data
        recurso.carrera_id = form.carrera.data
        recurso.materia_id = form.materia.data
        recurso.categoria = form.categoria.data
        recurso.disponibilidad = form.disponibilidad.data

        # Actualizar datos específicos según el tipo de recurso
        if recurso.resource_type == 'Link':
            recurso.external_link = form.url.data
        elif recurso.resource_type == 'Video':
            recurso.youtube_link = form.youtube_url.data

        # Guardar los cambios
        db.session.commit()

        # Verificar si la solicitud es AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'recurso': {
                    'id': recurso.id,
                    'title': recurso.title,
                    'description': recurso.description,
                    'external_link': recurso.external_link if recurso.resource_type == 'Link' else None,
                    'youtube_link': recurso.youtube_link if recurso.resource_type == 'Video' else None
                }
            }), 200
        else:
            # Si la solicitud no es AJAX, redireccionar al usuario
            flash('Recurso actualizado correctamente.', 'success')
            return redirect(url_for('app_bp.gestionar_recursos'))

    # Si el formulario no es válido, devolver los errores como JSON si la solicitud es AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'error': form.errors}), 400
    else:
        # Manejar errores si la solicitud no es AJAX
        flash('Ocurrió un error al actualizar el recurso. Revisa los campos e inténtalo de nuevo.', 'danger')
        return redirect(url_for('app_bp.gestionar_recursos'))

# Ruta para gestionar los recursos (solo docentes)
@app_bp.route('/gestionar-recursos', methods=['GET', 'POST'])
@login_required
def gestionar_recursos():
    if not current_user.tipo_usuario == 'docente':
        flash('No tienes permiso para acceder a esta página.', 'danger')
        return redirect(url_for('app_bp.index'))

    # Crear instancias de los formularios
    link_form = UploadLinkForm()
    file_form = UploadResourceForm()
    video_form = UploadVideoForm()

    # Filtrar carreras y materias para el docente actual
    carreras = Carrera.query.filter_by(id=current_user.carrera_id).all()
    materias = Materia.query.filter(Materia.carrera_id == current_user.carrera_id).all()

    # Ajustar las opciones de carrera y materia en los formularios de subida
    link_form.carrera.choices = [(carrera.id, carrera.nombre) for carrera in carreras]
    link_form.materia.choices = [(materia.id, materia.nombre) for materia in materias]
    file_form.carrera.choices = [(carrera.id, carrera.nombre) for carrera in carreras]
    file_form.materia.choices = [(materia.id, materia.nombre) for materia in materias]
    video_form.carrera.choices = [(carrera.id, carrera.nombre) for carrera in carreras]
    video_form.materia.choices = [(materia.id, materia.nombre) for materia in materias]

    # Obtener los recursos subidos por el docente con JOIN a carrera y materia
    recursos_links = db.session.query(Recurso).join(Carrera).join(Materia).filter(
        Recurso.uploaded_by == current_user.id,
        Recurso.resource_type == 'Link'
    ).all()

    recursos_archivos = db.session.query(Recurso).join(Carrera).join(Materia).filter(
        Recurso.uploaded_by == current_user.id,
        Recurso.resource_type == 'Archivo'
    ).all()

    recursos_videos = db.session.query(Recurso).join(Carrera).join(Materia).filter(
        Recurso.uploaded_by == current_user.id,
        Recurso.resource_type == 'Video'
    ).all()


    # Crear un diccionario de formularios específicos para cada recurso (links, archivos y videos)
    edit_link_forms = {recurso.id: EditLinkForm(obj=recurso) for recurso in recursos_links}
    edit_file_forms = {recurso.id: EditResourceForm(obj=recurso) for recurso in recursos_archivos}
    edit_video_forms = {recurso.id: EditVideoForm(obj=recurso) for recurso in recursos_videos}

    # Ajustar las opciones de carrera y materia en los formularios de edición
    for form in edit_link_forms.values():
        form.carrera.choices = [(carrera.id, carrera.nombre) for carrera in carreras]
        form.materia.choices = [(materia.id, materia.nombre) for materia in materias]

    for form in edit_file_forms.values():
        form.carrera.choices = [(carrera.id, carrera.nombre) for carrera in carreras]
        form.materia.choices = [(materia.id, materia.nombre) for materia in materias]

    for form in edit_video_forms.values():
        form.carrera.choices = [(carrera.id, carrera.nombre) for carrera in carreras]
        form.materia.choices = [(materia.id, materia.nombre) for materia in materias]

    # Pasar los formularios al contexto de la plantilla
    return render_template(
        'subir_recursos.html',
        recursos_links=recursos_links,
        recursos_archivos=recursos_archivos,
        recursos_videos=recursos_videos,
        link_form=link_form,
        file_form=file_form,
        video_form=video_form,
        edit_link_forms=edit_link_forms,
        edit_file_forms=edit_file_forms,
        edit_video_forms=edit_video_forms,
        materias=materias,
        carreras=carreras
    )



# Ruta para subir enlaces (solo docentes)
@app_bp.route('/subir-enlace', methods=['POST'])
@login_required
def subir_enlace():
    if not current_user.tipo_usuario == 'docente':
        flash('No tienes permiso para acceder a esta página.', 'danger')
        return redirect(url_for('app_bp.index'))

    title = request.form.get('title')
    description = request.form.get('description')
    url = request.form.get('url')
    categoria = request.form.get('categoria')
    carrera_id = request.form.get('carrera')
    materia_id = request.form.get('materia')
    disponibilidad = request.form.get('disponibilidad')

    # Validar que todos los campos requeridos estén completos
    if not title or not url or not categoria or not carrera_id or not materia_id or not disponibilidad:
        flash('Por favor, completa todos los campos requeridos.', 'danger')
        return redirect(url_for('app_bp.gestionar_recursos'))

    # Comprobar si ya existe un recurso con el mismo título
    if Recurso.query.filter_by(title=title, uploaded_by=current_user.id).first():
        flash('Ya existe un recurso con este título. Por favor, elige un título diferente.', 'danger')
        return redirect(url_for('app_bp.gestionar_recursos'))

    # Crear el nuevo recurso si no existe duplicado
    nuevo_recurso = Recurso(
        title=title,
        description=description,
        external_link=url,
        resource_type='Link',
        categoria=categoria,
        disponibilidad=disponibilidad,
        uploaded_by=current_user.id,
        carrera_id=carrera_id,
        materia_id=materia_id
    )

    db.session.add(nuevo_recurso)
    db.session.commit()
    flash('Enlace añadido exitosamente.', 'success')
    return redirect(url_for('app_bp.gestionar_recursos'))

# Ruta para subir archivos (solo docentes)
@app_bp.route('/subir-archivo', methods=['POST'])
@login_required
def subir_archivo():
    if not current_user.tipo_usuario == 'docente':
        flash('No tienes permiso para acceder a esta página.', 'danger')
        return redirect(url_for('app_bp.index'))

    title = request.form.get('title')
    description = request.form.get('description')
    categoria = request.form.get('categoria')
    carrera_id = request.form.get('carrera')
    materia_id = request.form.get('materia')
    disponibilidad = request.form.get('disponibilidad')
    file = request.files.get('archivo')

    # Validar archivo y campos requeridos
    if not file or not file.filename.endswith('.pdf'):
        flash('Por favor, sube un archivo PDF válido.', 'danger')
        return redirect(url_for('app_bp.gestionar_recursos'))

    if not title or not categoria or not carrera_id or not materia_id or not disponibilidad:
        flash('Por favor, completa todos los campos requeridos.', 'danger')
        return redirect(url_for('app_bp.gestionar_recursos'))

    # Comprobar si ya existe un recurso con el mismo título
    if Recurso.query.filter_by(title=title, uploaded_by=current_user.id).first():
        flash('Ya existe un recurso con este título. Por favor, elige un título diferente.', 'danger')
        return redirect(url_for('app_bp.gestionar_recursos'))

    # Guardar el archivo
    filename = secure_filename(file.filename)
    file_path = guardar_archivo_categoria(file, "Archivos", filename)

    # Crear el nuevo recurso de tipo archivo
    nuevo_recurso = Recurso(
        title=title,
        description=description,
        file_path=file_path,
        resource_type='Archivo',
        categoria=categoria,
        disponibilidad=disponibilidad,
        uploaded_by=current_user.id,
        carrera_id=carrera_id,
        materia_id=materia_id
    )

    db.session.add(nuevo_recurso)
    db.session.commit()
    flash('Archivo PDF subido exitosamente.', 'success')
    return redirect(url_for('app_bp.gestionar_recursos'))

# Ruta para subir videos de YouTube (solo docentes)
@app_bp.route('/subir-video', methods=['POST'])
@login_required
def subir_video():
    if not current_user.tipo_usuario == 'docente':
        flash('No tienes permiso para acceder a esta página.', 'danger')
        return redirect(url_for('app_bp.index'))

    title = request.form.get('title')
    description = request.form.get('description')
    youtube_url = request.form.get('youtube_url')
    categoria = request.form.get('categoria')
    carrera_id = request.form.get('carrera')
    materia_id = request.form.get('materia')
    disponibilidad = request.form.get('disponibilidad')

    # Validar campos requeridos
    if not title or not youtube_url or not categoria or not carrera_id or not materia_id or not disponibilidad:
        flash('Por favor, completa todos los campos requeridos.', 'danger')
        return redirect(url_for('app_bp.gestionar_recursos'))

    # Normalizar el enlace de YouTube antes de guardarlo
    youtube_url = ValidacionService.normalizar_youtube_link(youtube_url)

    # Comprobar si ya existe un recurso con el mismo título
    if Recurso.query.filter_by(title=title, uploaded_by=current_user.id).first():
        flash('Ya existe un recurso con este título. Por favor, elige un título diferente.', 'danger')
        return redirect(url_for('app_bp.gestionar_recursos'))

    # Crear el nuevo recurso de tipo video
    nuevo_recurso = Recurso(
        title=title,
        description=description,
        youtube_link=youtube_url,
        resource_type='Video',
        categoria=categoria,
        disponibilidad=disponibilidad,
        uploaded_by=current_user.id,
        carrera_id=carrera_id,
        materia_id=materia_id
    )

    db.session.add(nuevo_recurso)
    db.session.commit()
    flash('Video añadido exitosamente.', 'success')
    return redirect(url_for('app_bp.gestionar_recursos'))

# Función para guardar el archivo en la carpeta correspondiente a la categoría
def guardar_archivo_categoria(file, categoria, filename):
    categoria_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], categoria.lower())
    if not os.path.exists(categoria_folder):
        os.makedirs(categoria_folder)
    file_path = os.path.join(categoria_folder, filename)
    file.save(file_path)
    return file_path

# Ruta para ver archivos PDF en una ventana del navegador
@app_bp.route('/ver-pdf/<int:pdf_id>', methods=['GET'])
def ver_pdf(pdf_id):
    recurso = Recurso.query.get_or_404(pdf_id)
    
    # Verificar que el recurso sea de tipo archivo PDF
    if recurso.resource_type != 'Archivo':
        flash('Este recurso no es un archivo PDF.', 'danger')
        return redirect(url_for('app_bp.ejercicios_estudiantes'))
    
    # Registrar acceso al recurso
    AnalyticsService.registrar_acceso_recurso(recurso.id)
    
    # Retornar el archivo PDF para ser visualizado en el navegador
    return send_file(recurso.file_path, mimetype='application/pdf')

# Ruta para descargar un archivo PDF
@app_bp.route('/download-pdf/<int:pdf_id>', methods=['GET'])
@login_required
def download_pdf(pdf_id):
    recurso = Recurso.query.get_or_404(pdf_id)
    
    # Verificar si el recurso existe y si el archivo está disponible
    if not recurso.file_path or not os.path.exists(recurso.file_path):
        flash('El archivo solicitado no se encuentra disponible.', 'danger')
        return redirect(url_for('app_bp.gestionar_recursos'))

    # Registrar acceso al recurso
    AnalyticsService.registrar_acceso_recurso(recurso.id)

    return send_file(recurso.file_path, as_attachment=True)


# Ruta para mostrar la página de Docentes
@app_bp.route('/docentes')
def docentes():
    # Obtener todos los docentes registrados en la base de datos
    docentes = User.query.filter_by(tipo_usuario='docente').all()
    return render_template('docentes.html', docentes=docentes)

# Ruta para obtener la información del docente en formato JSON
@app_bp.route('/api/docente/<int:docente_id>')
def api_docente(docente_id):
    docente = User.query.get_or_404(docente_id)
    if docente.tipo_usuario != 'docente':
        abort(404)

    return jsonify({
        'nombre': docente.nombre,
        'apellido': docente.apellido,
        'tipo_usuario': docente.tipo_usuario,
        'redes_educativas': docente.redes_educativas,
        'articulos_publicados': docente.articulos_publicados,
        'carrera': docente.carrera.nombre,
        'materias': [materia.nombre for materia in docente.materias]
    })



def obtener_recursos_filtrados(categoria, tipos_recursos=['Archivo', 'Link', 'Video']):
    """
    Función genérica para obtener recursos filtrados por categoría.
    Elimina duplicación de código en las rutas de ejercicios, exámenes, etc.
    """
    # Obtener carreras y materias según el tipo de usuario
    carreras = RecursoService.obtener_carreras_para_usuario()
    
    # Obtener filtros desde la URL
    carrera_id = request.args.get('carrera', type=int)
    materia_id = request.args.get('materia', type=int)
    
    # Inicializar variables
    materias = []
    recursos = []
    carrera_seleccionada = None
    materia_seleccionada = None
    
    # Obtener materias según carrera seleccionada
    if carrera_id:
        carrera_seleccionada = Carrera.query.get(carrera_id)
        materias = RecursoService.obtener_materias_para_usuario(carrera_id)
    elif current_user.is_authenticated and current_user.is_estudiante:
        materias = RecursoService.obtener_materias_para_usuario()
    
    # Obtener recursos si hay filtros aplicados
    if materia_id:
        materia_seleccionada = Materia.query.get(materia_id)
        recursos = RecursoService.obtener_recursos_por_categoria(
            categoria, 
            carrera_id=carrera_id, 
            materia_id=materia_id
        )
        # Filtrar por tipos de recursos permitidos
        recursos = RecursoService.filtrar_recursos_por_tipo(recursos, tipos_recursos)
    
    return {
        'carreras': carreras,
        'materias': materias,
        'recursos': recursos,
        'carrera_seleccionada': carrera_seleccionada,
        'materia_seleccionada': materia_seleccionada,
        'carrera_id_seleccionada': carrera_id,
        'materia_id_seleccionada': materia_id
    }


# Ruta para mostrar videos con filtros por carrera y materia
@app_bp.route('/videos-estudiantes', methods=['GET'])
def videos_estudiantes():
    datos = obtener_recursos_filtrados('Videos', tipos_recursos=['Video'])
    return render_template('videos_estudiantes.html', **datos)


# Ruta para mostrar ejercicios con filtros por carrera y materia
@app_bp.route('/ejercicios-estudiantes', methods=['GET'])
def ejercicios_estudiantes():
    datos = obtener_recursos_filtrados('Ejercicios', tipos_recursos=['Archivo', 'Link'])
    return render_template('ejercicios_estudiantes.html', **datos)

# Ruta para mostrar exámenes con filtros por carrera y materia
@app_bp.route('/examenes-estudiantes', methods=['GET'])
def examenes_estudiantes():
    datos = obtener_recursos_filtrados('Exámenes', tipos_recursos=['Archivo', 'Link'])
    return render_template('examenes_estudiantes.html', **datos)

# Ruta para mostrar aplicaciones con filtros por carrera y materia
@app_bp.route('/aplicaciones-estudiantes', methods=['GET'])
def aplicaciones_estudiantes():
    datos = obtener_recursos_filtrados('Aplicaciones', tipos_recursos=['Archivo', 'Link'])
    return render_template('aplicaciones_estudiantes.html', **datos)

# Ruta para mostrar bibliografía con filtros por carrera y materia
@app_bp.route('/bibliografia-estudiantes', methods=['GET'])
def bibliografia_estudiantes():
    datos = obtener_recursos_filtrados('Bibliografía', tipos_recursos=['Archivo', 'Link'])
    return render_template('bibliografia_estudiantes.html', **datos)


# Rutas adicionales
@app_bp.route('/chatboot', methods=['GET'])
@login_required
def chatboot():
    # Obtener filtros de carrera y materia desde la URL (si están presentes)
    carrera_id = request.args.get('carrera', type=int)
    materia_id = request.args.get('materia', type=int)

    # Consulta base para recursos de tipo enlace con categoría Chatbot
    query = Recurso.query.filter_by(resource_type='Link', categoria='Chatbot')

    # Aplicar filtros dinámicos si están seleccionados
    if carrera_id:
        query = query.filter_by(carrera_id=carrera_id)
    if materia_id:
        query = query.filter_by(materia_id=materia_id)

    # Obtener todos los recursos filtrados
    recursos_chatbot = query.all()

    # Obtener la lista de carreras y materias disponibles para los filtros
    carreras = Carrera.query.all()
    materias = Materia.query.all()

    # Obtener la carrera y materia seleccionadas (para mostrar en la plantilla)
    carrera_seleccionada = Carrera.query.get(carrera_id) if carrera_id else None
    materia_seleccionada = Materia.query.get(materia_id) if materia_id else None

    # Renderizar plantilla con los recursos de chatbot y filtros
    return render_template(
        'chatboot.html',
        recursos_chatbot=recursos_chatbot,
        carreras=carreras,
        materias=materias,
        carrera_id_seleccionada=carrera_id,
        materia_id_seleccionada=materia_id,
        carrera_seleccionada=carrera_seleccionada,
        materia_seleccionada=materia_seleccionada
    )

@app_bp.route('/recursos')
def recursos():
    return render_template('recursos.html')

@app_bp.route('/herramientas')
def herramientas():
    return render_template('herramientas.html')

@app_bp.route('/bibliografia', methods=['GET', 'POST'])
@login_required
def bibliografia():
    # Filtrar los recursos por el tipo de "PDF_Bibliografia"
    recursos_bibliografia = Recurso.query.filter_by(resource_type='PDF_Bibliografia').all()

    # Obtener las carreras y materias para el filtro
    carreras = Carrera.query.all()
    materias = Materia.query.all()

    return render_template('bibliografia.html', carreras=carreras, materias=materias, recursos=recursos_bibliografia)

@app_bp.route('/videos-economia')
def videos_economia():
    return render_template('videos_economia.html')


# ==================== RUTAS API PARA PANEL DE ADMINISTRACIÓN ====================

@app_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Ruta para el panel de administración - Solo administradores"""
    if not current_user.is_administrador:
        flash('Acceso denegado. Solo los administradores pueden acceder al panel de administración.', 'danger')
        return redirect(url_for('app_bp.index'))
    
    # Obtener datos básicos para cargar la página
    from .models import User
    users = User.query.all()
    carreras = Carrera.query.all()
    
    return render_template('admin_dashboard.html', users=users, careers=carreras)


@app_bp.route('/api/admin/estadisticas', methods=['GET'])
@login_required
def api_estadisticas_generales():
    """API para obtener estadísticas generales del sistema - Solo administradores"""
    if not current_user.is_administrador:
        return jsonify({'error': 'Acceso denegado. Solo administradores'}), 403
    
    try:
        estadisticas = AnalyticsService.obtener_estadisticas_generales()
        return jsonify(estadisticas), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app_bp.route('/api/admin/recursos/populares', methods=['GET'])
@login_required
def api_recursos_populares():
    """API para obtener los recursos más populares - Solo administradores"""
    if not current_user.is_administrador:
        return jsonify({'error': 'Acceso denegado. Solo administradores'}), 403
    
    try:
        from .models import AccesoRecurso
        from sqlalchemy import func
        
        # Obtener top 20 recursos más accedidos
        recursos_populares = db.session.query(
            Recurso,
            func.count(AccesoRecurso.id).label('total_accesos')
        ).join(
            AccesoRecurso, Recurso.id == AccesoRecurso.recurso_id, isouter=True
        ).group_by(
            Recurso.id
        ).order_by(
            func.count(AccesoRecurso.id).desc()
        ).limit(20).all()
        
        resultado = [
            {
                'id': recurso.id,
                'titulo': recurso.title,
                'tipo': recurso.resource_type,
                'categoria': recurso.categoria,
                'carrera': recurso.carrera.nombre if recurso.carrera else 'N/A',
                'materia': recurso.materia.nombre if recurso.materia else 'N/A',
                'accesos': total_accesos or 0
            }
            for recurso, total_accesos in recursos_populares
        ]
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app_bp.route('/api/admin/recursos/por-carrera', methods=['GET'])
@login_required
def api_recursos_por_carrera():
    """API para obtener recursos filtrados por carrera - Solo administradores"""
    if not current_user.is_administrador:
        return jsonify({'error': 'Acceso denegado. Solo administradores'}), 403
    
    try:
        carrera_id = request.args.get('carrera_id', type=int)
        
        if carrera_id:
            recursos = Recurso.query.filter_by(carrera_id=carrera_id).all()
        else:
            recursos = Recurso.query.all()
        
        resultado = [
            {
                'id': r.id,
                'titulo': r.title,
                'tipo': r.resource_type,
                'categoria': r.categoria,
                'materia': r.materia.nombre if r.materia else 'N/A',
                'disponibilidad': r.disponibilidad,
                'fecha_subida': r.uploaded_at.strftime('%Y-%m-%d') if r.uploaded_at else 'N/A'
            }
            for r in recursos
        ]
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app_bp.route('/api/admin/usuarios/estadisticas', methods=['GET'])
@login_required
def api_usuarios_estadisticas():
    """API para obtener estadísticas de usuarios - Solo administradores"""
    if not current_user.is_administrador:
        return jsonify({'error': 'Acceso denegado. Solo administradores'}), 403
    
    try:
        from .models import User
        from sqlalchemy import func
        
        # Contar usuarios por tipo
        usuarios_por_tipo = db.session.query(
            User.tipo_usuario,
            func.count(User.id)
        ).group_by(User.tipo_usuario).all()
        
        # Contar usuarios por carrera
        usuarios_por_carrera = db.session.query(
            Carrera.nombre,
            func.count(User.id)
        ).join(User, Carrera.id == User.carrera_id).group_by(Carrera.nombre).all()
        
        resultado = {
            'por_tipo': {tipo: count for tipo, count in usuarios_por_tipo},
            'por_carrera': {carrera: count for carrera, count in usuarios_por_carrera}
        }
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app_bp.route('/api/admin/actividad/reciente', methods=['GET'])
@login_required
def api_actividad_reciente():
    """API para obtener actividad reciente del sistema - Solo administradores"""
    if not current_user.is_administrador:
        return jsonify({'error': 'Acceso denegado. Solo administradores'}), 403
    
    try:
        from .models import AccesoRecurso, SesionUsuario
        from datetime import datetime, timedelta
        
        # Obtener accesos recientes (últimas 24 horas)
        hace_24h = datetime.utcnow() - timedelta(hours=24)
        
        accesos_recientes = AccesoRecurso.query.filter(
            AccesoRecurso.fecha_acceso >= hace_24h
        ).order_by(AccesoRecurso.fecha_acceso.desc()).limit(50).all()
        
        sesiones_recientes = SesionUsuario.query.filter(
            SesionUsuario.fecha_inicio >= hace_24h
        ).order_by(SesionUsuario.fecha_inicio.desc()).limit(50).all()
        
        resultado = {
            'accesos': [
                {
                    'recurso': acceso.recurso.title if acceso.recurso else 'N/A',
                    'tipo_usuario': acceso.tipo_usuario,
                    'fecha': acceso.fecha_acceso.strftime('%Y-%m-%d %H:%M:%S')
                }
                for acceso in accesos_recientes
            ],
            'sesiones': [
                {
                    'tipo_usuario': sesion.tipo_usuario,
                    'usuario': sesion.usuario.nombre if sesion.usuario else 'Casual',
                    'fecha_inicio': sesion.fecha_inicio.strftime('%Y-%m-%d %H:%M:%S'),
                    'duracion': sesion.duracion_segundos if sesion.duracion_segundos else 'En curso'
                }
                for sesion in sesiones_recientes
            ]
        }
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app_bp.route('/api/admin/recursos/<int:recurso_id>/accesos', methods=['GET'])
@login_required
def api_recurso_accesos(recurso_id):
    """API para obtener estadísticas de acceso a un recurso específico - Solo administradores"""
    if not current_user.is_administrador:
        return jsonify({'error': 'Acceso denegado. Solo administradores'}), 403
    
    try:
        from .models import AccesoRecurso
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        recurso = Recurso.query.get_or_404(recurso_id)
        
        # Total de accesos
        total_accesos = AccesoRecurso.query.filter_by(recurso_id=recurso_id).count()
        
        # Accesos por tipo de usuario
        accesos_por_tipo = db.session.query(
            AccesoRecurso.tipo_usuario,
            func.count(AccesoRecurso.id)
        ).filter_by(recurso_id=recurso_id).group_by(AccesoRecurso.tipo_usuario).all()
        
        # Accesos en los últimos 7 días
        hace_7_dias = datetime.utcnow() - timedelta(days=7)
        accesos_recientes = AccesoRecurso.query.filter(
            AccesoRecurso.recurso_id == recurso_id,
            AccesoRecurso.fecha_acceso >= hace_7_dias
        ).count()
        
        resultado = {
            'recurso': {
                'id': recurso.id,
                'titulo': recurso.title,
                'tipo': recurso.resource_type,
                'categoria': recurso.categoria
            },
            'total_accesos': total_accesos,
            'accesos_por_tipo': {tipo: count for tipo, count in accesos_por_tipo},
            'accesos_ultimos_7_dias': accesos_recientes
        }
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



