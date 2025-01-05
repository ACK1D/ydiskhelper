#!/bin/bash
set -e

mkdir -p logs media staticfiles

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec granian --interface wsgi \
    --host 0.0.0.0 \
    --port 8000 \
    --workers ${GRANIAN_WORKERS:-2} \
    --threads ${GRANIAN_THREADS:-1} \
    ydiskhelper.wsgi:application 