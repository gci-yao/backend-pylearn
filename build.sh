#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Seed automatique si la base est vide
python manage.py shell -c "
from api.models import Level
if Level.objects.count() == 0:
    print('Base vide — seed en cours...')
    exec(open('api/seed.py').read())
else:
    print(f'Base déjà peuplée ({Level.objects.count()} niveaux) — seed ignoré.')
"

# Créer le superuser automatiquement si inexistant
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='legeny').exists():
    User.objects.create_superuser('legeny', 'legeny225@gmail.com', 'legeny225')
    print('Superuser créé : legeny / legeny225')
else:
    print('Superuser déjà existant.')
"