from data_Structure import app, db
# from flask_script import Manager

from flask import render_template, current_app, flash
from flask_migrate import Migrate, init, migrate, stamp, upgrade
import os

MIGRATIONS_FOLDER = "migrations/migrations/"


migration = Migrate(app, db, render_as_batch=True)


# manager = Manager(app)
# manager.add_command('db', MigrateCommand)
def migrate_database():
    if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), MIGRATIONS_FOLDER)):
        init(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), MIGRATIONS_FOLDER))
    stamp(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), MIGRATIONS_FOLDER), revision='head')
    try:
        migrate(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), MIGRATIONS_FOLDER))
    except:
        flash('Database could not be migrated!','danger')
    upgrade(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), MIGRATIONS_FOLDER))

# if __name__ == '__main__':
#    manager.run()
