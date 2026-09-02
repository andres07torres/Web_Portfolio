#!/bin/sh
set -e

# Timeout de 30 segundos para esperar PostgreSQL
TIMEOUT=30
COUNTER=0

echo "⏳ Esperando a PostgreSQL (máximo ${TIMEOUT}s)..."
until python -c "
import os, psycopg2
psycopg2.connect(
    host=os.environ['DB_HOST'],
    port=os.environ.get('DB_PORT', '5432'),
    dbname=os.environ['DB_NAME'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
)" 2>/dev/null; do
  COUNTER=$((COUNTER + 2))
  if [ $COUNTER -ge $TIMEOUT ]; then
    echo "⚠️  PostgreSQL no disponible después de ${TIMEOUT}s, continuando sin migraciones..."
    break
  fi
  echo "   PostgreSQL no disponible aún, reintentando en 2s... (${COUNTER}/${TIMEOUT})"
  sleep 2
done

if [ $COUNTER -lt $TIMEOUT ]; then
  echo "✅ PostgreSQL listo."
  echo "⚙️  Aplicando migraciones..."
  python manage.py migrate --noinput

  echo "📦 Recolectando archivos estáticos..."
  python manage.py collectstatic --noinput

  echo "👤 Sincronizando superusuario (creando o actualizando)..."
  python manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'K#m9&Lp2$vQ!5zR*8wN_x7Y')

u, created = User.objects.get_or_create(username=username)
u.set_password(password)
u.email = email
u.is_superuser = True
u.is_staff = True
u.save()

if created:
    print(f"✅ Superusuario '{username}' creado exitosamente.")
else:
    print(f"🔄 Superusuario '{username}' actualizado con las credenciales del .env.")
EOF
fi

# Render asigna el puerto dinámicamente via $PORT (default 8000 para local/Docker)
PORT="${PORT:-8000}"

echo "🚀 Iniciando Gunicorn en puerto $PORT..."
exec gunicorn portafolio.wsgi:application \
    --bind "0.0.0.0:$PORT" \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
