from os.path import dirname
from invoke import run, task
from django.conf import settings
from django.contrib.auth import get_user_model


base = dirname(__file__)
DEFAULT_DB_NAME = settings.DATABASES['default']['NAME']
DEFAULT_USERNAME = 'dcho'
DEFAULT_EMAIL = 'dcho@scrollmotion.com'
DEFAULT_CLIENT_ID = 'GZP5HlyiBwalItizXJbpY6iBoJhVKjmde0FU1bCo'


@task
def test():
    run('simplestudio/manage.py test core customer')


@task
def clean(db=False, db_name=DEFAULT_DB_NAME):
    if db:
        print("Database {} is being dropped and recreated.".format(db_name))
        run("psql -c 'drop database {}'".format(db_name))
        run("psql -c 'create database {}'".format(db_name))


@task
def su(username=None, email=None):
    email = email or username or DEFAULT_EMAIL
    username = username or DEFAULT_USERNAME
    run("{}/manage.py createsuperuser --username={} --email={}".format(base, username, email).strip())


@task
def build(db=False, db_name=DEFAULT_DB_NAME, admin=False, username=None, email=None):
    clean(db, db_name)
    run("{}/manage.py makemigrations core customer".format(base))
    run("{}/manage.py migrate".format(base))
    if admin:
        su(username, email)
    else:
        run("{}/manage.py createsuperuser".format(base))


@task
def create_application(username=None, email=None):
    """
    This process must require a superuser.
    """
    def get_su():
        try:
            get_user_model().objects.filter(is_superuser=True)[0]
        except get_user_model().DoesNotExist:
            su(username, email)

    run("{}/manage.py create_oauth2_application".format(base))


@task
def reset(db=False, db_name=DEFAULT_DB_NAME, username=None, email=None):
    build(db=db, db_name=db_name, admin=True, username=username, email=email)
    create_application()
