#!/bin/sh

python manage.py makemigrations || true
python manage.py migrate
exec honcho start
