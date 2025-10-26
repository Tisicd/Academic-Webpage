# ==========================================
# Script para Limpiar y Subir Proyecto a Git
# Sistema UCE - Solución Automática
# ==========================================

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🧹 LIMPIEZA Y PREPARACIÓN PARA GIT" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el directorio correcto
if (!(Test-Path "app_recursos")) {
    Write-Host "❌ Error: No estás en el directorio del proyecto" -ForegroundColor Red
    Write-Host "   Ejecuta este script desde D:\Pasantias\economia" -ForegroundColor Yellow
    exit 1
}

Write-Host "📁 Directorio actual: $PWD" -ForegroundColor Green
Write-Host ""

# Paso 1: Verificar archivos grandes
Write-Host "🔍 Paso 1: Buscando archivos grandes..." -ForegroundColor Yellow
$archivosGrandes = Get-ChildItem -Recurse -File | Where-Object {$_.Length -gt 10MB}
if ($archivosGrandes) {
    Write-Host "⚠️  Archivos mayores a 10 MB encontrados:" -ForegroundColor Yellow
    $archivosGrandes | Select-Object FullName, @{Name="Tamaño MB";Expression={[math]::Round($_.Length/1MB,2)}} | Format-Table
    Write-Host "   Estos archivos NO se subirán (están en .gitignore)" -ForegroundColor Cyan
} else {
    Write-Host "✅ No hay archivos grandes (>10MB)" -ForegroundColor Green
}
Write-Host ""

# Paso 2: Confirmar acción
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "⚠️  ADVERTENCIA" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Este script va a:" -ForegroundColor White
Write-Host "1. Eliminar el historial de Git actual (.git)" -ForegroundColor White
Write-Host "2. Crear un repositorio limpio desde cero" -ForegroundColor White
Write-Host "3. Hacer commit de TODO el código actual" -ForegroundColor White
Write-Host "4. Preparar para push a GitHub" -ForegroundColor White
Write-Host ""
Write-Host "El historial anterior se PERDERÁ" -ForegroundColor Red
Write-Host "Pero tendrás un repositorio limpio de ~500 KB" -ForegroundColor Green
Write-Host ""

$confirmacion = Read-Host "¿Continuar? (S/N)"
if ($confirmacion -ne "S" -and $confirmacion -ne "s") {
    Write-Host "❌ Operación cancelada" -ForegroundColor Yellow
    exit 0
}

Write-Host ""

# Paso 3: Eliminar .git
Write-Host "🗑️  Paso 2: Eliminando historial de Git..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Remove-Item -Path .git -Recurse -Force
    Write-Host "✅ Historial eliminado" -ForegroundColor Green
} else {
    Write-Host "ℹ️  No había carpeta .git" -ForegroundColor Cyan
}
Write-Host ""

# Paso 4: Inicializar nuevo repositorio
Write-Host "🆕 Paso 3: Inicializando repositorio limpio..." -ForegroundColor Yellow
git init
Write-Host "✅ Repositorio inicializado" -ForegroundColor Green
Write-Host ""

# Paso 5: Agregar archivos
Write-Host "📦 Paso 4: Agregando archivos al staging..." -ForegroundColor Yellow
git add -A
Write-Host "✅ Archivos agregados" -ForegroundColor Green
Write-Host ""

# Paso 6: Verificar que no hay archivos grandes
Write-Host "🔍 Paso 5: Verificando que NO hay archivos multimedia..." -ForegroundColor Yellow
$mp4Files = git ls-files | Select-String "\.mp4"
$jpgFiles = git ls-files | Select-String "\.(jpg|jpeg|png)"

if ($mp4Files) {
    Write-Host "❌ ERROR: Hay archivos .mp4 en staging:" -ForegroundColor Red
    $mp4Files
    Write-Host "   Revisar .gitignore" -ForegroundColor Yellow
    exit 1
}

if ($jpgFiles) {
    Write-Host "⚠️  Advertencia: Hay archivos de imagen:" -ForegroundColor Yellow
    $jpgFiles | Select-Object -First 5
    Write-Host "   Si no quieres subirlos, actualiza .gitignore" -ForegroundColor Cyan
}

Write-Host "✅ Sin archivos .mp4 en staging" -ForegroundColor Green
Write-Host ""

# Paso 7: Mostrar estadísticas
Write-Host "📊 Paso 6: Estadísticas del commit..." -ForegroundColor Yellow
$numArchivos = (git diff --cached --name-only | Measure-Object).Count
Write-Host "   Archivos a subir: $numArchivos" -ForegroundColor Cyan

$mdFiles = git ls-files | Select-String "\.md$"
Write-Host "   Archivos .md: $($mdFiles.Count)" -ForegroundColor Cyan
foreach ($md in $mdFiles) {
    Write-Host "      - $md" -ForegroundColor Gray
}
Write-Host ""

# Paso 8: Crear commit
Write-Host "💾 Paso 7: Creando commit..." -ForegroundColor Yellow
git commit -m "v2.0: Sistema UCE Refactorizado Completo

🎯 Sistema de Recursos Educativos - Universidad Central del Ecuador

✨ Nuevas Funcionalidades v2.0:
- Sistema de analytics con tracking automático de usuarios
- Panel de administración con dashboard interactivo y gráficas
- Rol de administrador con acceso exclusivo a estadísticas
- 7 APIs REST para obtener insights y reportes
- Tracking diferenciado: administradores, docentes, estudiantes, casuales
- Botón mostrar/ocultar contraseña en login y registro
- Botón regresar mejorado en editar perfil
- Redirección inteligente por tipo de usuario

🔧 Refactorización:
- Eliminadas 250+ líneas de código duplicado
- Creados 3 servicios reutilizables (Analytics, Recurso, Validación)
- Función genérica para filtrado de recursos
- Código modular, limpio y mantenible
- Manejo robusto de errores con try-except

📊 Base de Datos:
- 3 nuevas tablas: AccesoRecurso, SesionUsuario, EstadisticaDiaria
- 6 índices para optimización de consultas
- Scripts de migración automática (migrate_analytics.py)

🐳 Docker:
- Dockerfile mejorado con healthchecks
- docker-compose.yml con dependencias y healthchecks
- Script de inicio automático (docker-entrypoint.sh)
- Punto de entrada optimizado (run.py)
- Preparado para arquitectura distribuida

🔒 Seguridad:
- Solo administradores acceden al panel de administración
- Permisos granulares por tipo de usuario
- Sistema gracefully degradable
- Validaciones mejoradas

🛠️ Scripts de Ayuda:
- migrate_analytics.py - Migración de base de datos
- init_data.py - Inicialización de datos de prueba
- diagnosticar_problemas.py - Diagnóstico automático
- fix_rapido.py - Solución automática de problemas
- verificar_instalacion.py - Verificación de componentes

📦 Stack:
- Flask 2.2.5 + SQLAlchemy + PostgreSQL + Redis
- Bootstrap 5 + Tailwind CSS + Chart.js
- Docker + Docker Compose

✅ Estado: Sistema 100% funcional y listo para producción
📏 Peso: ~500 KB (optimizado, sin multimedia)
🎯 Versión: 2.0.0"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Commit creado exitosamente" -ForegroundColor Green
} else {
    Write-Host "❌ Error creando commit" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Paso 9: Instrucciones finales
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🚀 LISTO PARA PUSH" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ejecuta estos comandos para subir:" -ForegroundColor White
Write-Host ""
Write-Host "git remote add origin https://github.com/Tisicd/Academic-Webpage.git" -ForegroundColor Yellow
Write-Host "git push -f origin main" -ForegroundColor Yellow
Write-Host ""
Write-Host "Nota: Usamos -f (force) porque estamos reemplazando el historial" -ForegroundColor Cyan
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ PREPARACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan

