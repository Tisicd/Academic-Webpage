"""
Script de verificación post-instalación
Verifica que todas las mejoras estén correctamente implementadas
"""

import sys
import os

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def verificar_instalacion():
    """Verifica que todos los componentes estén correctamente instalados"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DEL SISTEMA")
    print("=" * 60)
    print()
    
    errores = []
    warnings = []
    
    # 1. Verificar imports
    print("📦 1. Verificando imports...")
    try:
        from app_recursos.app import create_app
        from app_recursos.app.models import (
            db, User, Carrera, Materia, Recurso,
            AccesoRecurso, SesionUsuario, EstadisticaDiaria
        )
        from app_recursos.app.services import (
            AnalyticsService, RecursoService, ValidacionService
        )
        print("   ✅ Todos los imports son correctos")
    except ImportError as e:
        print(f"   ❌ Error en imports: {e}")
        errores.append(f"Error de import: {e}")
    
    # 2. Verificar estructura de archivos
    print("\n📁 2. Verificando estructura de archivos...")
    archivos_requeridos = [
        'app_recursos/app/__init__.py',
        'app_recursos/app/models.py',
        'app_recursos/app/routes.py',
        'app_recursos/app/services.py',
        'app_recursos/app/forms.py',
        'app_recursos/app/config.py',
        'app_recursos/app/templates/admin_dashboard.html',
        'migrate_analytics.py',
        'README.md',
        'CHANGELOG.md',
        'MEJORAS_IMPLEMENTADAS.md'
    ]
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - NO ENCONTRADO")
            errores.append(f"Archivo faltante: {archivo}")
    
    # 3. Verificar app puede crearse
    print("\n🚀 3. Verificando creación de aplicación...")
    try:
        from app_recursos.app import create_app
        app = create_app()
        print("   ✅ Aplicación Flask creada correctamente")
        
        # 4. Verificar rutas
        print("\n🌐 4. Verificando rutas...")
        with app.app_context():
            rutas_esperadas = [
                'app_bp.admin_dashboard',
                'app_bp.api_estadisticas_generales',
                'app_bp.api_recursos_populares',
                'app_bp.api_recursos_por_carrera',
                'app_bp.api_usuarios_estadisticas',
                'app_bp.api_actividad_reciente',
                'app_bp.api_recurso_accesos'
            ]
            
            for endpoint in rutas_esperadas:
                try:
                    url = app.url_map._rules_by_endpoint.get(endpoint)
                    if url:
                        print(f"   ✅ {endpoint}")
                    else:
                        print(f"   ⚠️  {endpoint} - No encontrado")
                        warnings.append(f"Ruta no encontrada: {endpoint}")
                except:
                    print(f"   ⚠️  {endpoint} - Error al verificar")
            
            # 5. Verificar modelos
            print("\n🗄️  5. Verificando modelos de base de datos...")
            try:
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tablas = inspector.get_table_names()
                
                tablas_esperadas = [
                    'users',
                    'carreras',
                    'materias',
                    'recursos',
                    'acceso_recursos',
                    'sesiones_usuarios',
                    'estadisticas_diarias'
                ]
                
                for tabla in tablas_esperadas:
                    if tabla in tablas:
                        print(f"   ✅ {tabla}")
                    else:
                        print(f"   ⚠️  {tabla} - No encontrada (ejecutar migrate_analytics.py)")
                        warnings.append(f"Tabla no encontrada: {tabla}")
                
            except Exception as e:
                print(f"   ⚠️  No se pudo conectar a la base de datos: {e}")
                warnings.append("No se pudo verificar la base de datos")
            
            # 6. Verificar servicios
            print("\n⚙️  6. Verificando servicios...")
            try:
                from app_recursos.app.services import (
                    AnalyticsService, RecursoService, ValidacionService
                )
                
                # Verificar métodos de AnalyticsService
                metodos_analytics = [
                    'obtener_tipo_usuario',
                    'registrar_acceso_recurso',
                    'registrar_inicio_sesion',
                    'registrar_fin_sesion',
                    'actualizar_estadisticas_diarias',
                    'obtener_estadisticas_generales'
                ]
                
                for metodo in metodos_analytics:
                    if hasattr(AnalyticsService, metodo):
                        print(f"   ✅ AnalyticsService.{metodo}")
                    else:
                        print(f"   ❌ AnalyticsService.{metodo} - No encontrado")
                        errores.append(f"Método faltante: AnalyticsService.{metodo}")
                
                # Verificar métodos de RecursoService
                metodos_recurso = [
                    'obtener_recursos_por_categoria',
                    'obtener_carreras_para_usuario',
                    'obtener_materias_para_usuario',
                    'filtrar_recursos_por_tipo'
                ]
                
                for metodo in metodos_recurso:
                    if hasattr(RecursoService, metodo):
                        print(f"   ✅ RecursoService.{metodo}")
                    else:
                        print(f"   ❌ RecursoService.{metodo} - No encontrado")
                        errores.append(f"Método faltante: RecursoService.{metodo}")
                
                # Verificar métodos de ValidacionService
                metodos_validacion = [
                    'validar_cedula_ecuatoriana',
                    'normalizar_youtube_link'
                ]
                
                for metodo in metodos_validacion:
                    if hasattr(ValidacionService, metodo):
                        print(f"   ✅ ValidacionService.{metodo}")
                    else:
                        print(f"   ❌ ValidacionService.{metodo} - No encontrado")
                        errores.append(f"Método faltante: ValidacionService.{metodo}")
                        
            except Exception as e:
                print(f"   ❌ Error verificando servicios: {e}")
                errores.append(f"Error en servicios: {e}")
    
    except Exception as e:
        print(f"   ❌ Error creando aplicación: {e}")
        errores.append(f"Error al crear app: {e}")
        import traceback
        traceback.print_exc()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    if not errores and not warnings:
        print("\n🎉 ¡TODO ESTÁ CORRECTO!")
        print("✅ Todos los componentes están instalados y funcionando")
        print("\n📝 Próximos pasos:")
        print("   1. Ejecutar: python migrate_analytics.py")
        print("   2. Iniciar la aplicación: cd app_recursos && python -m flask run")
        print("   3. Acceder al panel: http://localhost:5000/admin/dashboard")
        return True
    else:
        if errores:
            print(f"\n❌ Se encontraron {len(errores)} errores:")
            for error in errores:
                print(f"   - {error}")
        
        if warnings:
            print(f"\n⚠️  Se encontraron {len(warnings)} advertencias:")
            for warning in warnings:
                print(f"   - {warning}")
        
        print("\n💡 Recomendaciones:")
        if warnings and not errores:
            print("   - Ejecutar migrate_analytics.py para crear las tablas faltantes")
        if errores:
            print("   - Revisar los errores listados arriba")
            print("   - Verificar que todas las dependencias estén instaladas")
            print("   - Consultar README.md para más información")
        
        return False

if __name__ == '__main__':
    try:
        resultado = verificar_instalacion()
        sys.exit(0 if resultado else 1)
    except Exception as e:
        print(f"\n💥 Error crítico durante la verificación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

