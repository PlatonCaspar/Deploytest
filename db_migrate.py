from migrate.versioning import api
from Platinen import app
from data_Structure import db
import os.path

SQLALCHEMY_DATABASE_URI = app['SQLALCHEMY_DATABASE_URI']
SQLALCHEMY_MIGRATE_REPO = 'static/Database/database_rep.sql'


def create_databases():
    db.create_all()
    if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
        api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    else:
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))
