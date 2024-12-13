#!/usr/bin/env bash
# exit on error
set -o errexit

pip install Django
pip install djangorestframework
pip install apscheduler
pip install whitenoise
pip install gunicorn
pip install python-dotenv
pip install openpyxl
pip install requests
pip install python-dotenv

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate
