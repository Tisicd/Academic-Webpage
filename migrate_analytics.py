"""
Script de migración para crear las tablas de analytics
Ejecutar este script después de actualizar el código para crear las nuevas tablas
"""

import os
import sys

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app_recursos.app import create_app
from app_recursos.app.models import db, AccesoRecurso, SesionUsuario, EstadisticaDiaria


def migrate_database():
    """Crea las nuevas tablas de analytics en la base de datos"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Iniciando migración de la base de datos...")
        
        try:
            # Crear todas las tablas (solo creará las que no existan)
            db.create_all()
            print("✅ Tablas de analytics creadas exitosamente:")
            print("   - acceso_recursos")
            print("   - sesiones_usuarios")
            print("   - estadisticas_diarias")
            
            # Verificar que las tablas existen
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\n📋 Tablas existentes en la base de datos: {len(tables)}")
            for table in sorted(tables):
                print(f"   - {table}")
            
            print("\n✅ Migración completada exitosamente!")
            print("\n💡 Las nuevas funcionalidades de analytics ya están disponibles:")
            print("   - Tracking de accesos a recursos")
            print("   - Registro de sesiones por tipo de usuario")
            print("   - Estadísticas agregadas diarias")
            print("   - Panel de administración con insights")
            
        except Exception as e:
            print(f"❌ Error durante la migración: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    migrate_database()

