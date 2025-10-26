"""
Punto de entrada principal para la aplicación
Compatible con Flask CLI, Gunicorn y Docker
"""

import os
import sys

# Asegurar que el directorio actual está en el path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app_recursos.app import create_app

# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    # Modo desarrollo local
    app.run(host='0.0.0.0', port=5000, debug=True)

