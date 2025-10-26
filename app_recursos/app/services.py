"""
Servicios para manejar lógica de negocio y evitar código repetido
"""
from flask import request
from flask_login import current_user
from datetime import datetime, date
from .models import db, AccesoRecurso, SesionUsuario, EstadisticaDiaria, Recurso, Carrera, Materia
from sqlalchemy import func, distinct


class AnalyticsService:
    """Servicio para manejar el tracking de analytics"""
    
    @staticmethod
    def obtener_tipo_usuario():
        """Determina el tipo de usuario actual"""
        if current_user.is_authenticated:
            return current_user.tipo_usuario
        return 'casual'
    
    @staticmethod
    def registrar_acceso_recurso(recurso_id):
        """Registra el acceso a un recurso"""
        try:
            tipo_usuario = AnalyticsService.obtener_tipo_usuario()
            user_id = current_user.id if current_user.is_authenticated else None
            
            acceso = AccesoRecurso(
                recurso_id=recurso_id,
                user_id=user_id,
                tipo_usuario=tipo_usuario,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:255]
            )
            
            db.session.add(acceso)
            db.session.commit()
            
            # Actualizar estadísticas diarias
            AnalyticsService.actualizar_estadisticas_diarias()
        except Exception as e:
            print(f"Error registrando acceso a recurso {recurso_id}: {e}")
            db.session.rollback()
    
    @staticmethod
    def registrar_inicio_sesion(user_id=None, session_id=None):
        """Registra el inicio de una sesión"""
        try:
            tipo_usuario = AnalyticsService.obtener_tipo_usuario()
            
            sesion = SesionUsuario(
                user_id=user_id,
                tipo_usuario=tipo_usuario,
                session_id=session_id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:255]
            )
            
            db.session.add(sesion)
            db.session.commit()
            
            # Actualizar estadísticas diarias
            AnalyticsService.actualizar_estadisticas_diarias()
            
            return sesion
        except Exception as e:
            print(f"Error registrando inicio de sesión: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def registrar_fin_sesion(session_id):
        """Registra el fin de una sesión"""
        try:
            sesion = SesionUsuario.query.filter_by(
                session_id=session_id,
                fecha_fin=None
            ).first()
            
            if sesion:
                sesion.fecha_fin = datetime.utcnow()
                sesion.duracion_segundos = int((sesion.fecha_fin - sesion.fecha_inicio).total_seconds())
                db.session.commit()
        except Exception as e:
            print(f"Error registrando fin de sesión: {e}")
            db.session.rollback()
    
    @staticmethod
    def actualizar_estadisticas_diarias():
        """Actualiza las estadísticas agregadas del día actual"""
        try:
            hoy = date.today()
            
            # Buscar o crear estadística del día
            estadistica = EstadisticaDiaria.query.filter_by(fecha=hoy).first()
            if not estadistica:
                estadistica = EstadisticaDiaria(fecha=hoy)
                db.session.add(estadistica)
            
            # Contar sesiones del día
            sesiones_hoy = SesionUsuario.query.filter(
                func.date(SesionUsuario.fecha_inicio) == hoy
            )
            
            estadistica.sesiones_total = sesiones_hoy.count()
            estadistica.sesiones_docentes = sesiones_hoy.filter_by(tipo_usuario='docente').count()
            estadistica.sesiones_estudiantes = sesiones_hoy.filter_by(tipo_usuario='estudiante').count()
            estadistica.sesiones_casuales = sesiones_hoy.filter_by(tipo_usuario='casual').count()
            
            # Contar accesos a recursos del día
            accesos_hoy = AccesoRecurso.query.filter(
                func.date(AccesoRecurso.fecha_acceso) == hoy
            )
            
            estadistica.accesos_recursos_total = accesos_hoy.count()
            estadistica.accesos_recursos_docentes = accesos_hoy.filter_by(tipo_usuario='docente').count()
            estadistica.accesos_recursos_estudiantes = accesos_hoy.filter_by(tipo_usuario='estudiante').count()
            estadistica.accesos_recursos_casuales = accesos_hoy.filter_by(tipo_usuario='casual').count()
            
            # Contar usuarios únicos del día
            from .models import User
            estadistica.usuarios_unicos_total = db.session.query(
                distinct(SesionUsuario.user_id)
            ).filter(
                func.date(SesionUsuario.fecha_inicio) == hoy,
                SesionUsuario.user_id.isnot(None)
            ).count()
            
            estadistica.usuarios_docentes = db.session.query(
                distinct(SesionUsuario.user_id)
            ).filter(
                func.date(SesionUsuario.fecha_inicio) == hoy,
                SesionUsuario.tipo_usuario == 'docente',
                SesionUsuario.user_id.isnot(None)
            ).count()
            
            estadistica.usuarios_estudiantes = db.session.query(
                distinct(SesionUsuario.user_id)
            ).filter(
                func.date(SesionUsuario.fecha_inicio) == hoy,
                SesionUsuario.tipo_usuario == 'estudiante',
                SesionUsuario.user_id.isnot(None)
            ).count()
            
            estadistica.updated_at = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            print(f"Error actualizando estadísticas diarias: {e}")
            db.session.rollback()
    
    @staticmethod
    def obtener_estadisticas_generales():
        """Obtiene estadísticas generales del sistema"""
        try:
            from .models import User
            
            # Estadísticas de usuarios
            total_usuarios = User.query.count()
            total_docentes = User.query.filter_by(tipo_usuario='docente').count()
            total_estudiantes = User.query.filter_by(tipo_usuario='estudiante').count()
            
            # Estadísticas de recursos
            total_recursos = Recurso.query.count()
            recursos_por_tipo = db.session.query(
                Recurso.resource_type,
                func.count(Recurso.id)
            ).group_by(Recurso.resource_type).all()
            
            recursos_por_categoria = db.session.query(
                Recurso.categoria,
                func.count(Recurso.id)
            ).group_by(Recurso.categoria).all()
            
            # Estadísticas de hoy
            hoy = date.today()
            estadistica_hoy = EstadisticaDiaria.query.filter_by(fecha=hoy).first()
            
            # Estadísticas de los últimos 7 días
            from datetime import timedelta
            hace_7_dias = hoy - timedelta(days=7)
            estadisticas_semana = EstadisticaDiaria.query.filter(
                EstadisticaDiaria.fecha >= hace_7_dias
            ).order_by(EstadisticaDiaria.fecha.desc()).all()
            
            # Recursos más accedidos (top 10)
            recursos_populares = db.session.query(
                Recurso,
                func.count(AccesoRecurso.id).label('total_accesos')
            ).join(
                AccesoRecurso, Recurso.id == AccesoRecurso.recurso_id
            ).group_by(
                Recurso.id
            ).order_by(
                func.count(AccesoRecurso.id).desc()
            ).limit(10).all()
            
            return {
                'usuarios': {
                    'total': total_usuarios,
                    'docentes': total_docentes,
                    'estudiantes': total_estudiantes
                },
                'recursos': {
                    'total': total_recursos,
                    'por_tipo': dict(recursos_por_tipo),
                    'por_categoria': dict(recursos_por_categoria)
                },
                'hoy': {
                    'sesiones_total': estadistica_hoy.sesiones_total if estadistica_hoy else 0,
                    'sesiones_docentes': estadistica_hoy.sesiones_docentes if estadistica_hoy else 0,
                    'sesiones_estudiantes': estadistica_hoy.sesiones_estudiantes if estadistica_hoy else 0,
                    'sesiones_casuales': estadistica_hoy.sesiones_casuales if estadistica_hoy else 0,
                    'accesos_recursos': estadistica_hoy.accesos_recursos_total if estadistica_hoy else 0,
                    'usuarios_unicos': estadistica_hoy.usuarios_unicos_total if estadistica_hoy else 0
                },
                'ultimos_7_dias': [
                    {
                        'fecha': est.fecha.isoformat(),
                        'sesiones_total': est.sesiones_total,
                        'sesiones_docentes': est.sesiones_docentes,
                        'sesiones_estudiantes': est.sesiones_estudiantes,
                        'sesiones_casuales': est.sesiones_casuales,
                        'accesos_recursos': est.accesos_recursos_total
                    }
                    for est in estadisticas_semana
                ],
                'recursos_populares': [
                    {
                        'id': recurso.id,
                        'titulo': recurso.title,
                        'tipo': recurso.resource_type,
                        'categoria': recurso.categoria,
                        'accesos': total_accesos
                    }
                    for recurso, total_accesos in recursos_populares
                ]
            }
        except Exception as e:
            print(f"Error obteniendo estadísticas generales: {e}")
            # Retornar estadísticas vacías si hay error
            return {
                'usuarios': {'total': 0, 'docentes': 0, 'estudiantes': 0},
                'recursos': {'total': 0, 'por_tipo': {}, 'por_categoria': {}},
                'hoy': {
                    'sesiones_total': 0, 'sesiones_docentes': 0,
                    'sesiones_estudiantes': 0, 'sesiones_casuales': 0,
                    'accesos_recursos': 0, 'usuarios_unicos': 0
                },
                'ultimos_7_dias': [],
                'recursos_populares': []
            }


class RecursoService:
    """Servicio para manejar la lógica de recursos"""
    
    @staticmethod
    def obtener_recursos_por_categoria(categoria, carrera_id=None, materia_id=None):
        """
        Obtiene recursos filtrados por categoría, con filtros opcionales de carrera y materia.
        Maneja la lógica según el tipo de usuario.
        """
        query = Recurso.query.filter_by(categoria=categoria)
        
        if current_user.is_authenticated:
            if current_user.is_estudiante:
                # Estudiantes ven recursos de su carrera
                query = query.filter_by(carrera_id=current_user.carrera_id)
                if materia_id:
                    query = query.filter_by(materia_id=materia_id)
            elif current_user.is_docente:
                # Docentes ven sus propios recursos
                if carrera_id and materia_id:
                    query = query.filter_by(
                        carrera_id=carrera_id,
                        materia_id=materia_id,
                        uploaded_by=current_user.id
                    )
                else:
                    query = query.filter_by(uploaded_by=current_user.id)
        else:
            # Usuarios casuales ven solo recursos públicos
            query = query.filter_by(disponibilidad='publica')
            if carrera_id:
                query = query.filter_by(carrera_id=carrera_id)
            if materia_id:
                query = query.filter_by(materia_id=materia_id)
        
        return query.all()
    
    @staticmethod
    def obtener_carreras_para_usuario():
        """Obtiene las carreras que el usuario puede ver"""
        if current_user.is_authenticated:
            if current_user.is_estudiante:
                return [current_user.carrera]
            elif current_user.is_docente:
                return Carrera.query.filter_by(id=current_user.carrera_id).all()
        return Carrera.query.all()
    
    @staticmethod
    def obtener_materias_para_usuario(carrera_id=None):
        """Obtiene las materias que el usuario puede ver"""
        if current_user.is_authenticated:
            if current_user.is_estudiante:
                return Materia.query.filter_by(carrera_id=current_user.carrera_id).all()
            elif current_user.is_docente:
                if carrera_id:
                    return Materia.query.filter_by(carrera_id=carrera_id).all()
                return current_user.materias
        
        if carrera_id:
            return Materia.query.filter_by(carrera_id=carrera_id).all()
        return Materia.query.all()
    
    @staticmethod
    def filtrar_recursos_por_tipo(recursos, tipos_permitidos):
        """Filtra recursos por tipo"""
        return [r for r in recursos if r.resource_type in tipos_permitidos]


class ValidacionService:
    """Servicio para validaciones comunes"""
    
    @staticmethod
    def validar_cedula_ecuatoriana(cedula):
        """Valida una cédula ecuatoriana"""
        if len(cedula) != 10:
            return False
        try:
            digitos = [int(d) for d in cedula]
        except ValueError:
            return False

        # Los dos primeros dígitos corresponden a la provincia (01 - 24)
        provincia = int(cedula[:2])
        if provincia < 1 or provincia > 24:
            return False

        # El tercer dígito debe ser menor que 6 para personas naturales
        if digitos[2] >= 6:
            return False

        # Algoritmo de verificación de la cédula
        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        suma = 0
        for i in range(9):
            valor = coeficientes[i] * digitos[i]
            if valor >= 10:
                valor -= 9
            suma += valor

        verificador = 10 - (suma % 10) if suma % 10 != 0 else 0
        return digitos[-1] == verificador
    
    @staticmethod
    def normalizar_youtube_link(youtube_url):
        """Normaliza enlaces de YouTube a formato embed"""
        import re
        patrones = [
            r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})'
        ]

        for patron in patrones:
            match = re.search(patron, youtube_url)
            if match:
                video_id = match.group(1)
                return f'https://www.youtube.com/embed/{video_id}'
        
        return youtube_url

