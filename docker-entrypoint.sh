#!/bin/sh
set -e

# Timeout para esperar PostgreSQL
TIMEOUT=45
COUNTER=0

echo "⏳ Esperando a que PostgreSQL esté listo..."
until python -c "
import os, sys, psycopg2
try:
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        import dj_database_url
        cfg = dj_database_url.parse(db_url)
        psycopg2.connect(
            host=cfg.get('HOST', 'db'),
            port=cfg.get('PORT', 5432),
            dbname=cfg.get('NAME', 'postgres'),
            user=cfg.get('USER', 'postgres'),
            password=cfg.get('PASSWORD', '')
        )
    else:
        psycopg2.connect(
            host=os.environ.get('DB_HOST', 'db'),
            port=os.environ.get('DB_PORT', '5432'),
            dbname=os.environ.get('DB_NAME', 'postgres'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', '')
        )
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
  COUNTER=$((COUNTER + 2))
  if [ $COUNTER -ge $TIMEOUT ]; then
    echo "⚠️ PostgreSQL no respondió tras ${TIMEOUT}s. Continuando..."
    break
  fi
  echo "   Esperando conexión a PostgreSQL... (${COUNTER}/${TIMEOUT}s)"
  sleep 2
done

if [ $COUNTER -lt $TIMEOUT ]; then
  echo "✅ PostgreSQL conectado exitosamente."
  echo "⚙️ Aplicando migraciones de base de datos..."
  python manage.py migrate --noinput

  echo "📦 Recolectando archivos estáticos..."
  python manage.py collectstatic --noinput

  echo "👤 Verificando y configurando superusuario..."
  python manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Tigre6788')

try:
    u, created = User.objects.get_or_create(username=username)
    u.set_password(password)
    u.email = email
    u.is_superuser = True
    u.is_staff = True
    u.save()
    if created:
        print(f"✅ Superusuario '{username}' creado exitosamente.")
    else:
        print(f"🔄 Superusuario '{username}' actualizado correctamente.")
except Exception as e:
    print(f"⚠️ Error al crear/actualizar superusuario: {e}")
EOF
fi

PORT="${PORT:-8000}"

echo "🚀 Iniciando Gunicorn en el puerto $PORT..."
exec gunicorn portafolio.wsgi:application \
    --bind "0.0.0.0:$PORT" \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
