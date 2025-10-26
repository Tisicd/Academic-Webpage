"""
Script de diagnóstico para identificar problemas en el sistema
Ejecutar este script para verificar configuración y detectar errores
"""

import sys
import os

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def diagnosticar():
    """Diagnostica problemas comunes del sistema"""
    print("=" * 70)
    print("🔍 DIAGNÓSTICO DEL SISTEMA")
    print("=" * 70)
    print()
    
    problemas = []
    advertencias = []
    
    # 1. Verificar imports
    print("📦 1. Verificando imports y dependencias...")
    try:
        from app_recursos.app import create_app
        from app_recursos.app.models import (
            db, User, Carrera, Materia, Recurso,
            AccesoRecurso, SesionUsuario, EstadisticaDiaria
        )
        print("   ✅ Imports correctos")
    except ImportError as e:
        print(f"   ❌ Error en imports: {e}")
        problemas.append(f"Import error: {e}")
        return
    
    # 2. Crear aplicación
    print("\n🚀 2. Creando aplicación Flask...")
    try:
        app = create_app()
        print("   ✅ Aplicación creada")
    except Exception as e:
        print(f"   ❌ Error creando app: {e}")
        problemas.append(f"Error al crear app: {e}")
        import traceback
        traceback.print_exc()
        return
    
    with app.app_context():
        # 3. Verificar conexión a base de datos
        print("\n🗄️  3. Verificando conexión a base de datos...")
        try:
            from sqlalchemy import inspect, text
            
            # Intentar una consulta simple
            result = db.session.execute(text("SELECT 1")).fetchone()
            print("   ✅ Conexión a base de datos exitosa")
            
            # Verificar tablas
            inspector = inspect(db.engine)
            tablas = inspector.get_table_names()
            print(f"   ℹ️  Tablas encontradas: {len(tablas)}")
            
            tablas_requeridas = {
                'users': False,
                'carreras': False,
                'materias': False,
                'recursos': False,
                'acceso_recursos': False,
                'sesiones_usuarios': False,
                'estadisticas_diarias': False
            }
            
            for tabla in tablas_requeridas.keys():
                if tabla in tablas:
                    tablas_requeridas[tabla] = True
                    print(f"      ✅ {tabla}")
                else:
                    print(f"      ❌ {tabla} - NO EXISTE")
                    problemas.append(f"Tabla faltante: {tabla}")
            
        except Exception as e:
            print(f"   ❌ Error de conexión: {e}")
            problemas.append(f"Error de BD: {e}")
            import traceback
            traceback.print_exc()
        
        # 4. Verificar usuario administrador
        print("\n👨‍💼 4. Verificando usuario administrador...")
        try:
            admin = User.query.filter_by(tipo_usuario='administrador').first()
            if admin:
                print(f"   ✅ Usuario administrador encontrado:")
                print(f"      Email: {admin.email}")
                print(f"      Nombre: {admin.nombre} {admin.apellido}")
                print(f"      ID: {admin.id}")
                
                # Verificar propiedad is_administrador
                if hasattr(admin, 'is_administrador') and admin.is_administrador:
                    print(f"      ✅ Propiedad is_administrador: True")
                else:
                    print(f"      ❌ Propiedad is_administrador no funciona")
                    problemas.append("Propiedad is_administrador no funciona")
            else:
                print("   ❌ NO se encontró usuario administrador")
                print("      ⚠️  Ejecutar: python init_data.py")
                advertencias.append("Usuario administrador no existe")
        except Exception as e:
            print(f"   ❌ Error verificando administrador: {e}")
            problemas.append(f"Error verificando admin: {e}")
        
        # 5. Verificar rutas
        print("\n🌐 5. Verificando rutas críticas...")
        rutas_criticas = [
            ('app_bp.login', '/login'),
            ('app_bp.admin_dashboard', '/admin/dashboard'),
            ('app_bp.api_estadisticas_generales', '/api/admin/estadisticas')
        ]
        
        for endpoint, path_esperado in rutas_criticas:
            try:
                url = app.url_for(endpoint)
                print(f"   ✅ {endpoint} → {url}")
            except Exception as e:
                print(f"   ❌ {endpoint} - Error: {e}")
                problemas.append(f"Ruta faltante: {endpoint}")
        
        # 6. Verificar Redis
        print("\n🔴 6. Verificando conexión a Redis...")
        try:
            from redis import Redis
            redis_url = os.getenv('SESSION_REDIS', 'redis://localhost:6379/0')
            redis_client = Redis.from_url(redis_url)
            redis_client.ping()
            print(f"   ✅ Redis conectado: {redis_url}")
        except Exception as e:
            print(f"   ⚠️  Redis no disponible: {e}")
            advertencias.append("Redis no está corriendo (necesario para sesiones)")
        
        # 7. Probar login simulado
        print("\n🔐 7. Probando autenticación...")
        try:
            test_user = User.query.filter_by(email='admin@uce.edu.ec').first()
            if test_user:
                # Probar verificación de contraseña
                if test_user.check_password('admin123'):
                    print("   ✅ Contraseña del admin verifica correctamente")
                else:
                    print("   ❌ Contraseña del admin NO verifica")
                    problemas.append("Password check falla para admin")
                
                # Verificar tipo de usuario
                print(f"   ℹ️  Tipo de usuario: {test_user.tipo_usuario}")
                print(f"   ℹ️  is_administrador: {test_user.is_administrador}")
            else:
                print("   ❌ Usuario admin@uce.edu.ec no encontrado")
                problemas.append("Usuario admin no existe")
        except Exception as e:
            print(f"   ❌ Error probando auth: {e}")
            problemas.append(f"Error en auth: {e}")
        
        # 8. Verificar servicios
        print("\n⚙️  8. Verificando servicios de analytics...")
        try:
            from app_recursos.app.services import AnalyticsService
            
            # Probar obtener_estadisticas_generales
            stats = AnalyticsService.obtener_estadisticas_generales()
            if stats:
                print("   ✅ AnalyticsService.obtener_estadisticas_generales() funciona")
                print(f"      Total usuarios: {stats['usuarios']['total']}")
                print(f"      Total recursos: {stats['recursos']['total']}")
            else:
                print("   ⚠️  obtener_estadisticas_generales() retorna None")
        except Exception as e:
            print(f"   ⚠️  Error en AnalyticsService: {e}")
            advertencias.append(f"Analytics service error: {e}")
            import traceback
            traceback.print_exc()
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 70)
    
    if not problemas and not advertencias:
        print("\n🎉 ¡TODO ESTÁ CORRECTO!")
        print("✅ El sistema debería funcionar correctamente")
        print("\n📝 Próximos pasos:")
        print("   1. Si aún hay problemas, verificar logs de Flask al iniciar sesión")
        print("   2. Abrir consola del navegador (F12) y buscar errores JavaScript")
        print("   3. Verificar que Redis esté corriendo")
        return True
    else:
        if problemas:
            print(f"\n❌ PROBLEMAS CRÍTICOS ENCONTRADOS ({len(problemas)}):")
            for i, problema in enumerate(problemas, 1):
                print(f"   {i}. {problema}")
        
        if advertencias:
            print(f"\n⚠️  ADVERTENCIAS ({len(advertencias)}):")
            for i, advertencia in enumerate(advertencias, 1):
                print(f"   {i}. {advertencia}")
        
        print("\n💡 SOLUCIONES SUGERIDAS:")
        
        if any('tabla faltante' in p.lower() for p in problemas):
            print("\n   🔧 Tablas faltantes:")
            print("      python migrate_analytics.py")
        
        if any('usuario admin' in p.lower() or 'admin no existe' in p.lower() for p in problemas):
            print("\n   🔧 Usuario administrador faltante:")
            print("      python init_data.py")
        
        if any('redis' in a.lower() for a in advertencias):
            print("\n   🔧 Redis no está corriendo:")
            print("      Windows: Iniciar servicio de Redis")
            print("      Linux/Mac: redis-server")
        
        return False

if __name__ == '__main__':
    try:
        resultado = diagnosticar()
        
        print("\n" + "=" * 70)
        if resultado:
            print("✅ Diagnóstico completado - Sistema OK")
            sys.exit(0)
        else:
            print("⚠️  Diagnóstico completado - Revisar problemas arriba")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error crítico durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

