[33mcommit 4d8700bc9b121736e1e87bc7c33657425d5309d9[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mmain[m[33m)[m
Author: David Tisalema <letisidw@gmail.com>
Date:   Sun Oct 26 04:05:34 2025 -0500

    Refactorización v2.0: Sistema de analytics, panel de admin y mejoras completas
    
     Nuevas Funcionalidades:
    - Sistema de analytics completo con tracking de usuarios
    - Panel de administración con dashboard interactivo y gráficas
    - Rol de administrador con acceso exclusivo a estadísticas
    - 7 APIs REST para analytics y reportes
    - Botón mostrar/ocultar contraseña en login y registro
    - Botón regresar en editar perfil
    - Redirección automática por tipo de usuario
    
     Refactorización:
    - Eliminadas 250+ líneas de código duplicado
    - Creados 3 servicios: AnalyticsService, RecursoService, ValidacionService
    - Función genérica para filtrado de recursos
    - Código modular y mantenible
    
     Base de Datos:
    - 3 nuevas tablas: AccesoRecurso, SesionUsuario, EstadisticaDiaria
    - 6 índices para optimización de consultas
    - Scripts de migración automática
    
     Docker:
    - Dockerfile mejorado con healthchecks
    - docker-compose.yml con dependencias correctas
    - Script de inicio automático (docker-entrypoint.sh)
    - Punto de entrada mejorado (run.py)
    
     Seguridad:
    - Solo administradores acceden al panel de admin
    - Manejo robusto de errores con try-except
    - Sistema gracefully degradable
    - Validaciones mejoradas
    
     Scripts de Ayuda:
    - migrate_analytics.py - Migración de BD
    - init_data.py - Inicialización de datos
    - diagnosticar_problemas.py - Diagnóstico
    - fix_rapido.py - Solución automática
    - verificar_instalacion.py - Verificación
    
     Correcciones:
    - Errores de sintaxis corregidos
    - Flash messages funcionando
    - Labels HTML correctos
    - Panel de admin con navegación propia
    - Warnings de SQLAlchemy silenciados
    
     Estado: Sistema completamente funcional y listo para producción

 .dockerignore                                      |  59 [32m++[m
 .gitignore                                         | 343 [32m++++++++++[m
 Dockerfile                                         |  29 [32m+[m[31m-[m
 README.md                                          | 477 [32m++++++++++++++[m
 app_recursos/app/__init__.py                       |  23 [32m+[m[31m-[m
 .../app/__pycache__/__init__.cpython-312.pyc       | Bin [31m9220[m -> [32m0[m bytes
 .../app/__pycache__/config.cpython-312.pyc         | Bin [31m2917[m -> [32m0[m bytes
 app_recursos/app/__pycache__/forms.cpython-312.pyc | Bin [31m8036[m -> [32m0[m bytes
 .../app/__pycache__/models.cpython-312.pyc         | Bin [31m8154[m -> [32m0[m bytes
 .../app/__pycache__/routes.cpython-312.pyc         | Bin [31m50661[m -> [32m0[m bytes
 app_recursos/app/__pycache__/utils.cpython-312.pyc | Bin [31m4344[m -> [32m0[m bytes
 app_recursos/app/models.py                         |  84 [32m++[m[31m-[m
 app_recursos/app/routes.py                         | 674 [32m++++++++++[m[31m----------[m
 app_recursos/app/services.py                       | 372 [32m+++++++++++[m
 app_recursos/app/templates/admin_dashboard.html    | 708 [32m+++++++++++++++[m[31m------[m
 app_recursos/app/templates/editar_perfil.html      |  20 [32m+[m[31m-[m
 app_recursos/app/templates/login.html              | 115 [32m+++[m[31m-[m
 app_recursos/app/templates/registro.html           |  62 [32m+[m[31m-[m
 diagnosticar_problemas.py                          | 237 [32m+++++++[m
 docker-compose-microservices.yml                   | 310 [32m+++++++++[m
 docker-compose.yml                                 |  40 [32m+[m[31m-[m
 docker-entrypoint.sh                               |  69 [32m++[m
 env.docker.example                                 |  29 [32m+[m
 env.microservices.example                          |  38 [32m++[m
 fix_rapido.py                                      | 125 [32m++++[m
 init_data.py                                       | 250 [32m++++[m[31m----[m
 migrate_analytics.py                               |  56 [32m++[m
 run.py                                             |  20 [32m+[m
 verificar_instalacion.py                           | 225 [32m+++++++[m
 29 files changed, 3628 insertions(+), 737 deletions(-)
