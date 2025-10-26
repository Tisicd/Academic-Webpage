#!/bin/bash
# Script de inicio para contenedor Docker
# Ejecuta migraciones y luego inicia la aplicación

set -e

echo "========================================="
echo "🐳 INICIANDO CONTENEDOR UCE"
echo "========================================="

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a PostgreSQL..."
# Usar las variables de entorno del docker-compose
DB_HOST=${POSTGRES_HOST:-db}
DB_USER=${POSTGRES_USER:-uce_user}
DB_NAME=${POSTGRES_DB:-uce_economia_db}
DB_PASS=${POSTGRES_PASSWORD:-uce_password}

# Intentar conectar hasta 30 veces (1 minuto)
MAX_TRIES=30
TRIES=0
until PGPASSWORD=$DB_PASS psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null || [ $TRIES -eq $MAX_TRIES ]; do
  TRIES=$((TRIES+1))
  if [ $TRIES -eq $MAX_TRIES ]; then
    echo "❌ PostgreSQL no respondió después de $MAX_TRIES intentos"
    echo "⚠️  Iniciando aplicación de todas formas..."
    break
  fi
  echo "   PostgreSQL no está listo - esperando... (intento $TRIES/$MAX_TRIES)"
  sleep 2
done

if [ $TRIES -lt $MAX_TRIES ]; then
  echo "✅ PostgreSQL está listo"
fi

# Esperar a que Redis esté listo
echo "⏳ Esperando a Redis..."
TRIES=0
until redis-cli -h redis ping 2>/dev/null | grep -q PONG || [ $TRIES -eq 15 ]; do
  TRIES=$((TRIES+1))
  if [ $TRIES -eq 15 ]; then
    echo "❌ Redis no respondió"
    echo "⚠️  Iniciando aplicación de todas formas..."
    break
  fi
  echo "   Redis no está listo - esperando..."
  sleep 2
done

if [ $TRIES -lt 15 ]; then
  echo "✅ Redis está listo"
fi

# Ejecutar migraciones de base de datos
echo "📦 Ejecutando migraciones..."
python migrate_analytics.py 2>/dev/null || echo "⚠️  Migraciones ya ejecutadas o error (continuando...)"

# Inicializar datos si es necesario
echo "👥 Verificando usuarios iniciales..."
python init_data.py 2>/dev/null || echo "ℹ️  Datos ya inicializados"

echo "========================================="
echo "🚀 INICIANDO APLICACIÓN FLASK"
echo "========================================="

# Ejecutar la aplicación
exec python run.py

