#!/bin/bash
set -e

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py ensure_superuser
python manage.py seed_portfolio
python manage.py collectstatic --noinput
