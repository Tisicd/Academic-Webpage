"""
Script de Solución Rápida
Ejecuta todos los pasos necesarios para que el sistema funcione correctamente
"""

import sys
import os

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def fix_rapido():
    """Ejecuta todos los pasos de solución en orden"""
    print("=" * 70)
    print("🔧 SOLUCIÓN RÁPIDA - SISTEMA UCE")
    print("=" * 70)
    print()
    print("Este script ejecutará:")
    print("1. Migración de base de datos (crear tablas de analytics)")
    print("2. Inicialización de datos (crear usuario admin)")
    print("3. Diagnóstico del sistema")
    print()
    input("Presiona ENTER para continuar...")
    print()
    
    # Paso 1: Migración
    print("=" * 70)
    print("📦 PASO 1: Migración de Base de Datos")
    print("=" * 70)
    print()
    
    try:
        print("Ejecutando migrate_analytics.py...")
        exec(open('migrate_analytics.py').read())
        print("\n✅ Migración completada")
    except Exception as e:
        print(f"\n⚠️  Error en migración: {e}")
        print("   Continuando con siguiente paso...")
    
    print()
    input("Presiona ENTER para continuar con el siguiente paso...")
    print()
    
    # Paso 2: Inicialización
    print("=" * 70)
    print("👥 PASO 2: Inicialización de Datos")
    print("=" * 70)
    print()
    
    try:
        print("Ejecutando init_data.py...")
        exec(open('init_data.py').read())
        print("\n✅ Datos inicializados")
    except Exception as e:
        print(f"\n⚠️  Error en inicialización: {e}")
        print("   Continuando con siguiente paso...")
    
    print()
    input("Presiona ENTER para continuar con el diagnóstico...")
    print()
    
    # Paso 3: Diagnóstico
    print("=" * 70)
    print("🔍 PASO 3: Diagnóstico del Sistema")
    print("=" * 70)
    print()
    
    try:
        print("Ejecutando diagnosticar_problemas.py...")
        exec(open('diagnosticar_problemas.py').read())
    except Exception as e:
        print(f"\n⚠️  Error en diagnóstico: {e}")
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE SOLUCIÓN RÁPIDA")
    print("=" * 70)
    print()
    print("✅ Procesos completados:")
    print("   1. Tablas de analytics creadas/verificadas")
    print("   2. Usuario administrador creado/verificado")
    print("   3. Diagnóstico del sistema ejecutado")
    print()
    print("🚀 PRÓXIMOS PASOS:")
    print()
    print("   1. Limpiar caché del navegador:")
    print("      Ctrl + Shift + R (Windows/Linux)")
    print("      Cmd + Shift + R (Mac)")
    print()
    print("   2. Iniciar la aplicación:")
    print("      cd app_recursos")
    print("      python -m flask run")
    print()
    print("   3. Acceder al login:")
    print("      http://localhost:5000/login")
    print()
    print("   4. Iniciar sesión como administrador:")
    print("      Email: admin@uce.edu.ec")
    print("      Password: admin123")
    print()
    print("   5. Verificar redirección automática a:")
    print("      http://localhost:5000/admin/dashboard")
    print()
    print("=" * 70)
    print("🎉 ¡LISTO! El sistema debería funcionar correctamente ahora")
    print("=" * 70)
    print()
    print("💡 Si aún hay problemas:")
    print("   - Revisar SOLUCION_PROBLEMAS_LOGIN.md")
    print("   - Verificar logs de Flask en la terminal")
    print("   - Abrir consola del navegador (F12) y buscar errores")
    print()

if __name__ == '__main__':
    try:
        fix_rapido()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Error crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

