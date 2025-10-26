# Sistema de Recursos Educativos - UCE Ciencias Económicas

Sistema web para la gestión y distribución de recursos educativos en la Universidad Central del Ecuador, Facultad de Ciencias Económicas.

## 🚀 Características Principales

### Gestión de Recursos
- **Múltiples tipos de recursos**: PDFs, videos de YouTube, enlaces externos
- **Categorización avanzada**: Bibliografía, ejercicios, exámenes, aplicaciones, videos educativos, chatbots
- **Filtrado inteligente**: Por carrera, materia y categoría
- **Permisos granulares**: Recursos públicos y privados (solo estudiantes)

### Sistema de Usuarios
- **Tres tipos de usuarios**:
  - **Administradores**: Acceso completo al panel de administración y analytics
  - **Docentes**: Pueden subir y gestionar recursos
  - **Estudiantes**: Acceso a recursos según su carrera y materias
- **Usuarios casuales**: Acceso a recursos públicos sin registro
- **Autenticación segura**: Sistema de login con gestión de sesiones en Redis
- **Validación de identidad**: Validación de cédulas ecuatorianas
- **Registro restringido**: Solo correos @uce.edu.ec

### 📊 Sistema de Analytics (NUEVO v2.0)

#### Panel de Administración Avanzado
- **Dashboard interactivo** con gráficas en tiempo real
- **4 Cards informativos**: Usuarios, recursos, sesiones, accesos
- **Gráficas visuales**:
  - Distribución de sesiones por tipo de usuario (dona)
  - Distribución de recursos por tipo (circular)
  - Actividad de los últimos 7 días (líneas)
  - Usuarios por tipo y carrera (barras)
- **Top 20 recursos** más accedidos
- **Actividad reciente** de las últimas 24 horas
- **Actualización automática** cada 30 segundos

#### Tracking Automático
- **Registro de accesos a recursos**: Cada visualización/descarga
- **Sesiones de usuario**: Tracking de inicio y fin con duración
- **Diferenciación por tipo**: Administradores, docentes, estudiantes y casuales
- **Estadísticas diarias**: Pre-agregadas para consultas rápidas

## 🏗️ Arquitectura

### Stack Tecnológico

**Backend**:
- Flask 2.2.5
- SQLAlchemy (ORM)
- PostgreSQL (Base de datos)
- Redis (Gestión de sesiones y caché)
- Flask-Login (Autenticación)
- Flask-WTF (Formularios)
- Bcrypt (Hashing de contraseñas)

**Frontend**:
- HTML5/CSS3
- JavaScript (Vanilla)
- Bootstrap 5 (Sitio principal)
- Tailwind CSS (Panel de administración)
- Chart.js (Gráficas interactivas)
- Font Awesome (Iconos)

**DevOps**:
- Docker & Docker Compose
- Gunicorn (WSGI server para producción)

### Estructura de Servicios

El código está organizado en servicios reutilizables:

- **AnalyticsService**: Tracking y estadísticas
- **RecursoService**: Gestión de recursos educativos
- **ValidacionService**: Validaciones comunes

## 📦 Instalación

### Opción 1: Docker (Recomendado)

```bash
# 1. Clonar repositorio
git clone <url-del-repositorio>
cd economia

# 2. Crear archivo de configuración
cp env.docker.example .env
# Editar .env con tus credenciales

# 3. Construir y levantar contenedores
docker-compose build
docker-compose up -d

# 4. Inicializar datos
docker-compose exec web1 python init_data.py

# 5. Acceder al sistema
# http://localhost:5000
```

### Opción 2: Instalación Local

```bash
# 1. Clonar repositorio
git clone <url-del-repositorio>
cd economia

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
# Crear archivo .env en app_recursos/app/ con:
SECRET_KEY=tu_clave_secreta
SQLALCHEMY_DATABASE_URI=postgresql://usuario:password@localhost/nombre_bd
SESSION_REDIS=redis://localhost:6379/0
# ... más configuraciones

# 5. Ejecutar migraciones y crear datos
python migrate_analytics.py
python init_data.py

# 6. Iniciar aplicación
cd app_recursos
python -m flask run

# Acceder a: http://localhost:5000
```

## 👥 Usuarios de Prueba

Después de ejecutar `init_data.py`:

### Administrador
```
Email: admin@uce.edu.ec
Password: admin123
Acceso: Panel de administración completo
```

### Docentes
```
Docente 1: docente1@uce.edu.ec / password123 (Economía)
Docente 2: docente2@uce.edu.ec / password456 (Finanzas)
```

### Estudiantes
```
Estudiante 1: estudiante1@uce.edu.ec / password789 (Economía)
Estudiante 2: estudiante2@uce.edu.ec / password000 (Finanzas)
```

## 📊 API Endpoints

### Endpoints de Administración (Solo Administradores)

```
GET  /admin/dashboard                     - Panel de administración
GET  /api/admin/estadisticas              - Estadísticas generales
GET  /api/admin/recursos/populares        - Top 20 recursos más accedidos
GET  /api/admin/recursos/por-carrera      - Recursos filtrados por carrera
GET  /api/admin/usuarios/estadisticas     - Estadísticas de usuarios
GET  /api/admin/actividad/reciente        - Actividad de las últimas 24h
GET  /api/admin/recursos/<id>/accesos     - Estadísticas de recurso específico
```

## 🔒 Seguridad

- ✅ Protección CSRF en todos los formularios
- ✅ Validación de sesiones con Redis (sesión única por dispositivo)
- ✅ Validación de cédulas ecuatorianas (algoritmo oficial)
- ✅ Restricción de registro a correos institucionales (@uce.edu.ec)
- ✅ Bcrypt para hashing de contraseñas
- ✅ Tres niveles de permisos (administrador, docente, estudiante)
- ✅ Recursos públicos vs privados

## 📈 Mejoras Implementadas (v2.0)

### Refactorización
- ✅ Eliminadas 250+ líneas de código duplicado
- ✅ Servicios reutilizables (AnalyticsService, RecursoService, ValidacionService)
- ✅ Función genérica para filtrado de recursos
- ✅ Código modular y mantenible

### Nuevas Funcionalidades
- ✅ Sistema completo de analytics con 3 nuevas tablas de BD
- ✅ Panel de administración con dashboard interactivo
- ✅ Rol de administrador con permisos específicos
- ✅ Tracking automático de usuarios (diferenciando tipos)
- ✅ 7 APIs REST para estadísticas
- ✅ Botón mostrar/ocultar contraseña (login y registro)
- ✅ Botón regresar en editar perfil
- ✅ Mensajes flash mejorados con animaciones

### Optimizaciones
- ✅ 6 índices en base de datos para consultas rápidas
- ✅ Estadísticas pre-calculadas (EstadisticaDiaria)
- ✅ Consultas optimizadas con JOINs eficientes
- ✅ Manejo robusto de errores con try-except
- ✅ Sistema gracefully degradable

## 🐳 Docker

### Comandos Principales

```bash
# Levantar sistema
docker-compose up -d

# Ver logs
docker-compose logs -f web1

# Detener sistema
docker-compose down

# Reconstruir (después de cambios)
docker-compose build web1
docker-compose up -d

# Ejecutar scripts dentro del contenedor
docker-compose exec web1 python init_data.py
docker-compose exec web1 python migrate_analytics.py
```

### Healthchecks
Todos los servicios tienen healthchecks implementados para garantizar disponibilidad.

## 🛠️ Scripts de Utilidad

```bash
# Migración de base de datos (crear tablas de analytics)
python migrate_analytics.py

# Inicializar datos (crear usuarios y carreras)
python init_data.py

# Diagnóstico del sistema
python diagnosticar_problemas.py

# Solución rápida (ejecuta migración + inicialización + diagnóstico)
python fix_rapido.py

# Verificación de instalación
python verificar_instalacion.py
```

## 📁 Estructura del Proyecto

```
economia/
├── app_recursos/
│   ├── app/
│   │   ├── __init__.py          # Configuración de la app
│   │   ├── models.py            # Modelos de datos (7 tablas)
│   │   ├── routes.py            # Rutas y controladores
│   │   ├── services.py          # Lógica de negocio (NUEVO)
│   │   ├── forms.py             # Formularios WTForms
│   │   ├── utils.py             # Utilidades
│   │   ├── config.py            # Configuración
│   │   ├── static/              # CSS, JS, imágenes
│   │   └── templates/           # Plantillas HTML
├── migrate_analytics.py         # Script de migración
├── init_data.py                 # Script de inicialización
├── run.py                       # Punto de entrada
├── diagnosticar_problemas.py    # Diagnóstico
├── fix_rapido.py                # Solución automática
├── Dockerfile                   # Configuración Docker
├── docker-compose.yml           # Orquestación Docker
├── requirements.txt             # Dependencias Python
├── .gitignore                   # Archivos ignorados por Git
└── README.md                    # Este archivo
```

## 🔧 Configuración

### Variables de Entorno Requeridas

Crear archivo `.env` con:

```env
# Flask
SECRET_KEY=tu_clave_secreta_muy_segura
FLASK_ENV=development

# Base de Datos
POSTGRES_DB=nombre_base_datos
POSTGRES_USER=usuario
POSTGRES_PASSWORD=password
SQLALCHEMY_DATABASE_URI=postgresql://usuario:password@localhost/nombre_bd

# Redis
SESSION_REDIS=redis://localhost:6379/0
SESSION_EXPIRATION=7200

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_password_de_aplicacion
MAIL_DEFAULT_SENDER=tu_email@gmail.com
```

**Nota**: Para Gmail, crear una "Contraseña de aplicación" en configuración de seguridad.

## 📊 Modelos de Base de Datos

### Tablas Principales
- `users` - Usuarios del sistema
- `carreras` - Carreras académicas
- `materias` - Materias por carrera
- `recursos` - Recursos educativos

### Tablas de Analytics (v2.0)
- `acceso_recursos` - Registro de cada acceso a recursos
- `sesiones_usuarios` - Registro de sesiones con duración
- `estadisticas_diarias` - Estadísticas pre-agregadas por día

## 🎯 Uso del Sistema

### Para Administradores
1. Iniciar sesión → Redirección automática al panel de admin
2. Ver estadísticas del sistema en tiempo real
3. Monitorear uso de recursos
4. Identificar recursos más populares
5. Analizar patrones de uso por tipo de usuario

### Para Docentes
1. Iniciar sesión con credenciales institucionales
2. Acceder a "Gestionar Recursos"
3. Subir recursos (PDFs, videos, enlaces)
4. Editar y eliminar sus propios recursos
5. Categorizar y establecer disponibilidad

### Para Estudiantes
1. Registrarse con correo @uce.edu.ec
2. Seleccionar carrera y materias
3. Acceder a recursos filtrados por materia
4. Ver videos, descargar PDFs, acceder a enlaces
5. Editar perfil personal

### Para Usuarios Casuales
1. Navegar el sitio sin registro
2. Acceder solo a recursos públicos
3. Ver información de docentes y carreras

## 🚨 Solución de Problemas

### Docker no levanta
```bash
# Verificar servicios
docker-compose ps

# Ver logs
docker-compose logs web1

# Reconstruir
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Panel de admin no carga
```bash
# Verificar que existe usuario administrador
docker-compose exec db psql -U tu_usuario -d tu_db \
  -c "SELECT * FROM users WHERE tipo_usuario='administrador';"

# Si no existe, crear usuarios
docker-compose exec web1 python init_data.py
```

### Base de datos vacía
```bash
# Ejecutar migraciones y crear datos
docker-compose exec web1 python migrate_analytics.py
docker-compose exec web1 python init_data.py
```

## 🎓 Requisitos del Sistema

- **Docker & Docker Compose** (recomendado)
  
  O alternativamente:
- Python 3.8+
- PostgreSQL 13+
- Redis 6+

## 📞 Soporte

### Comandos de Diagnóstico

```bash
# Diagnóstico completo del sistema
python diagnosticar_problemas.py

# Solución automática de problemas comunes
python fix_rapido.py

# Verificar instalación
python verificar_instalacion.py
```

## 🔄 Actualización desde Versión Anterior

Si ya tenías el sistema instalado:

```bash
# 1. Hacer backup de la base de datos
docker-compose exec db pg_dump -U usuario nombre_db > backup.sql

# 2. Detener sistema actual
docker-compose down

# 3. Actualizar código (git pull o descargar nueva versión)

# 4. Reconstruir contenedores
docker-compose build

# 5. Levantar sistema
docker-compose up -d

# 6. Ejecutar migraciones
docker-compose exec web1 python migrate_analytics.py

# 7. Crear usuario administrador si no existe
docker-compose exec web1 python init_data.py
```

## 🌟 Nuevas Funcionalidades v2.0

- ✅ Sistema de analytics completo con 3 nuevas tablas
- ✅ Panel de administración con dashboard interactivo
- ✅ Rol de administrador con acceso exclusivo a estadísticas
- ✅ Tracking automático de todos los usuarios
- ✅ 7 APIs REST para obtener estadísticas
- ✅ Código refactorizado (-250 líneas duplicadas)
- ✅ Servicios organizados y reutilizables
- ✅ Mejoras de UX (mostrar contraseña, botón regresar)
- ✅ Manejo robusto de errores
- ✅ Sistema preparado para arquitectura distribuida

## 📝 Licencia

Este proyecto es propiedad de la Universidad Central del Ecuador - Facultad de Ciencias Económicas.

## 👨‍💻 Desarrollo

### Preparado para Escalar

El sistema está preparado para migrar a arquitectura de microservicios:
- Servicios bien definidos y desacoplados
- APIs internas implementadas
- Configuración multi-contenedor disponible
- Documentación de arquitectura distribuida

### Próximas Mejoras Planeadas

- [ ] Exportación de estadísticas a Excel/PDF
- [ ] Notificaciones en tiempo real
- [ ] Sistema de comentarios y valoraciones
- [ ] Búsqueda avanzada de recursos
- [ ] App móvil
- [ ] Migración a microservicios

## 🎉 Versión Actual

**Versión**: 2.0.0  
**Fecha**: Octubre 2025  
**Estado**: Q/A  
**Calidad**: ⭐⭐⭐⭐⭐

---

**Desarrollado con ❤️ para la comunidad educativa de la UCE**
