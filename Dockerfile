# Usa una imagen oficial de Python como base
FROM python:3.12-slim

# Instala las dependencias necesarias para PostgreSQL, Redis CLI y herramientas
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de requerimientos al directorio de trabajo
COPY requirements.txt .

# Instala las dependencias del archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido de la aplicación al contenedor
COPY . .

# Exponer el puerto 5000 para Flask
EXPOSE 5000

# Establece las variables de entorno
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=development

# Copiar y dar permisos al script de entrada
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Healthcheck para verificar que la aplicación está corriendo
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Punto de entrada
ENTRYPOINT ["docker-entrypoint.sh"]
