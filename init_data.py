"""
Script para inicializar datos de prueba en la base de datos
Crea carreras, materias y usuarios de prueba (docentes, estudiantes y administrador)
"""

from app_recursos.app import create_app
from app_recursos.app.models import db, Carrera, Materia, User
from flask_bcrypt import Bcrypt, generate_password_hash

# Inicializar la aplicación y bcrypt
app = create_app()
bcrypt = Bcrypt(app)

with app.app_context():
    # Crear las tablas si no existen
    db.create_all()
    print("✅ Tablas verificadas/creadas en la base de datos\n")

    # ==================== CARRERAS Y MATERIAS ====================
    if Carrera.query.count() == 0:
        print("📚 Agregando carreras y materias...")

        # Crear carreras
        carrera_economia = Carrera(nombre='Economía')
        carrera_finanzas = Carrera(nombre='Finanzas')
        carrera_estadistica = Carrera(nombre='Estadística')

        db.session.add_all([carrera_economia, carrera_finanzas, carrera_estadistica])
        db.session.commit()

        # Crear materias
        materias_economia = [
            Materia(nombre='Álgebra Lineal', carrera_id=carrera_economia.id),
            Materia(nombre='Matemática Básica', carrera_id=carrera_economia.id),
            Materia(nombre='Matemática I', carrera_id=carrera_economia.id),
            Materia(nombre='Matemática II', carrera_id=carrera_economia.id)
        ]
        materias_finanzas = [
            Materia(nombre='Matemática Básica', carrera_id=carrera_finanzas.id),
            Materia(nombre='Cálculo Diferencial', carrera_id=carrera_finanzas.id),
            Materia(nombre='Cálculo Integral', carrera_id=carrera_finanzas.id)
        ]
        materias_estadistica = [
            Materia(nombre='Cálculo I', carrera_id=carrera_estadistica.id),
            Materia(nombre='Cálculo II', carrera_id=carrera_estadistica.id),
            Materia(nombre='Cálculo III', carrera_id=carrera_estadistica.id),
            Materia(nombre='Álgebra Lineal', carrera_id=carrera_estadistica.id),
            Materia(nombre='Ecuaciones Diferenciales', carrera_id=carrera_estadistica.id)
        ]

        db.session.add_all(materias_economia + materias_finanzas + materias_estadistica)
        db.session.commit()
        print("   ✅ Carreras y materias creadas\n")
    else:
        print("📚 Carreras y materias ya existen\n")

    # Obtener carreras y materias (existan o no)
    carrera_economia = Carrera.query.filter_by(nombre='Economía').first()
    carrera_finanzas = Carrera.query.filter_by(nombre='Finanzas').first()
    
    algebra_lineal = Materia.query.filter_by(nombre='Álgebra Lineal').first()
    matematica_basica = Materia.query.filter_by(nombre='Matemática Básica').first()
    matematica_I = Materia.query.filter_by(nombre='Matemática I').first()
    calculo_diferencial = Materia.query.filter_by(nombre='Cálculo Diferencial').first()
    calculo_integral = Materia.query.filter_by(nombre='Cálculo Integral').first()

    # ==================== USUARIO ADMINISTRADOR ====================
    admin_exists = User.query.filter_by(tipo_usuario='administrador').first()
    
    if not admin_exists:
        print("👨‍💼 Creando usuario ADMINISTRADOR...")
        
        admin_user = User(
            username='admin',
            email='admin@uce.edu.ec',
            password_hash=generate_password_hash('admin123').decode('utf-8'),
            cedula='1700000000',
            nombre='Administrador',
            apellido='Sistema',
            carrera_id=carrera_economia.id,
            tipo_usuario='administrador'
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("   ✅ Usuario administrador creado exitosamente")
        print("      📧 Email: admin@uce.edu.ec")
        print("      🔑 Password: admin123")
        print("      👤 Tipo: administrador\n")
    else:
        print("👨‍💼 Usuario administrador YA EXISTE")
        print(f"      📧 Email: {admin_exists.email}\n")

    # ==================== DOCENTES ====================
    if User.query.filter_by(tipo_usuario='docente').count() == 0:
        print("👨‍🏫 Creando usuarios DOCENTES...")
        
        docente1 = User(
            username='docente1',
            email='docente1@uce.edu.ec',
            password_hash=generate_password_hash('password123').decode('utf-8'),
            cedula='1234567890',
            nombre='Juan',
            apellido='Pérez',
            carrera_id=carrera_economia.id,
            tipo_usuario='docente',
            redes_educativas='https://linkedin.com/in/juanperez',
            articulos_publicados='https://researchgate.net/juanperez'
        )
        docente1.materias.extend([algebra_lineal, matematica_basica])

        docente2 = User(
            username='docente2',
            email='docente2@uce.edu.ec',
            password_hash=generate_password_hash('password456').decode('utf-8'),
            cedula='0987654321',
            nombre='María',
            apellido='Gómez',
            carrera_id=carrera_finanzas.id,
            tipo_usuario='docente',
            redes_educativas='https://linkedin.com/in/mariagomez',
            articulos_publicados='https://researchgate.net/mariagomez'
        )
        docente2.materias.extend([calculo_diferencial, calculo_integral])

        db.session.add_all([docente1, docente2])
        db.session.commit()
        
        print("   ✅ Docentes creados")
        print("      📧 docente1@uce.edu.ec / password123")
        print("      📧 docente2@uce.edu.ec / password456\n")
    else:
        print("👨‍🏫 Docentes ya existen\n")

    # ==================== ESTUDIANTES ====================
    if User.query.filter_by(tipo_usuario='estudiante').count() == 0:
        print("👨‍🎓 Creando usuarios ESTUDIANTES...")
        
        estudiante1 = User(
            username='estudiante1',
            email='estudiante1@uce.edu.ec',
            password_hash=generate_password_hash('password789').decode('utf-8'),
            cedula='1122334455',
            nombre='Carlos',
            apellido='Sánchez',
            carrera_id=carrera_economia.id,
            tipo_usuario='estudiante'
        )
        estudiante1.materias.extend([algebra_lineal, matematica_I])

        estudiante2 = User(
            username='estudiante2',
            email='estudiante2@uce.edu.ec',
            password_hash=generate_password_hash('password000').decode('utf-8'),
            cedula='5566778899',
            nombre='Ana',
            apellido='Martínez',
            carrera_id=carrera_finanzas.id,
            tipo_usuario='estudiante'
        )
        estudiante2.materias.extend([calculo_diferencial])

        db.session.add_all([estudiante1, estudiante2])
        db.session.commit()
        
        print("   ✅ Estudiantes creados")
        print("      📧 estudiante1@uce.edu.ec / password789")
        print("      📧 estudiante2@uce.edu.ec / password000\n")
    else:
        print("👨‍🎓 Estudiantes ya existen\n")

    print("=" * 60)
    print("✅ INICIALIZACIÓN COMPLETADA")
    print("=" * 60)
    print("\n💡 Usuarios de Prueba Disponibles:\n")
    
    # Mostrar resumen de usuarios
    total_users = User.query.count()
    admin_count = User.query.filter_by(tipo_usuario='administrador').count()
    docente_count = User.query.filter_by(tipo_usuario='docente').count()
    estudiante_count = User.query.filter_by(tipo_usuario='estudiante').count()
    
    print(f"   📊 Total de usuarios: {total_users}")
    print(f"      👨‍💼 Administradores: {admin_count}")
    print(f"      👨‍🏫 Docentes: {docente_count}")
    print(f"      👨‍🎓 Estudiantes: {estudiante_count}")
    print("\n📊 Panel de administración: http://localhost:5000/admin/dashboard")
    print("   (Solo accesible para administradores)\n")
