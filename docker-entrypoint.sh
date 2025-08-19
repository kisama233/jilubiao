#!/bin/sh
set -e

# Start backend with gunicorn in background
cd /app/backend
export DB_HOST=${DB_HOST:-db}
export DB_USER=${DB_USER:-root}
export DB_PASSWORD=${DB_PASSWORD:-ki233}
export DB_NAME=${DB_NAME:-jilu_db}

# 使用 python -m gunicorn 明确执行
python -m gunicorn -b 0.0.0.0:5000 app:app --workers 2 &

# Start nginx (in foreground)
nginx -g 'daemon off;'