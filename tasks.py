from os.path import dirname
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connections
from invoke import run, task
from django.db.utils import OperationalError


base = dirname(__file__)
DEFAULT_DB_NAME = settings.DATABASES['default']['NAME']
DEFAULT_USERNAME = 'dcho'
DEFAULT_EMAIL = 'dcho@scrollmotion.com'
DEFAULT_CLIENT_ID = 'GZP5HlyiBwalItizXJbpY6iBoJhVKjmde0FU1bCo'
DEFAULT_APPS = ['core', 'customer', 'password', 'e_mail', 'content']


@task
def test(apps=None):
    '''
    Run django unittest
    '''
    if not apps:
        apps = ' '.join(DEFAULT_APPS)
    run('{}/manage.py test {}'.format(base, apps))


@task
def clean(db=False, db_name=DEFAULT_DB_NAME):
    '''
    If db is set to True, this process will drop the database if exists and
    recreate it.
    '''
    if db:
        print("Database {} is being dropped and recreated.".format(db_name))
        db_conn = connections['default']
        try:
            db_conn.cursor()
        except OperationalError:
            pass
        else:
            db_conn.close()
            run("psql -c 'drop database {}'".format(db_name))
        run("psql -c 'create database {}'".format(db_name))


@task
def su(username=None, email=None):
    '''
    Create a superuser
    '''
    email = email or username or DEFAULT_EMAIL
    username = username or DEFAULT_USERNAME
    run("{}/manage.py createsuperuser --username={} --email={}".format(base, username, email).strip())


@task
def build(db=False, db_name=DEFAULT_DB_NAME, admin=False, username=None, email=None):
    clean(db, db_name)
    run("{}/manage.py makemigrations {}".format(base, ' '.join(DEFAULT_APPS)))
    run("{}/manage.py migrate".format(base))
    if admin:
        su(username, email)
    else:
        run("{}/manage.py createsuperuser".format(base))


@task
def create_application(username=None, email=None):
    '''
    This process must require a superuser.
    '''
    def get_su():
        try:
            get_user_model().objects.filter(is_superuser=True)[0]
        except get_user_model().DoesNotExist:
            su(username, email)

    run("{}/manage.py create_oauth2_application".format(base))


@task
def import_flatpages(file=None, overwrite=False, info=False):
    '''
    Create email templates with using import_flatpages management command
    that imports a json file to the database.
    '''
    attrs = ""
    if file:
        attrs += " --file={}".format(file)
    if overwrite:
        attrs += " --overwrite=True"
    if info:
        attrs += " --info=True"
    run("{}/manage.py import_flatpages{}".format(base, attrs))


@task
def reset(db=False, db_name=DEFAULT_DB_NAME, username=None, email=None):
    build(db=db, db_name=db_name, admin=True, username=username, email=email)
    create_application()
    import_flatpages()
