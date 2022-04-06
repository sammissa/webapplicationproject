web: gunicorn webapplicationproject.wsgi
heroku ps:scale web=1
release: python manage.py migrate
