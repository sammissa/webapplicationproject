web: gunicorn webapplicationproject.wsgi
heroku ps:scale web=1
web: python manage.py makemigrations
web: python manage.py migrate