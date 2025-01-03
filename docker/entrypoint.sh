#!/bin/bash

mkdir -p logs staticfiles media

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec granian --interface wsgi \
    --host 0.0.0.0 \
    --port 8000 \
    --workers $GRANIAN_WORKERS \
    --threads $GRANIAN_THREADS \
    ydiskhelper.wsgi:application 