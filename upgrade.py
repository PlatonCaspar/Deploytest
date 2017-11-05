from data_Structure import app, db
# from flask_script import Manager

from flask import render_template, current_app, flash
from flask_migrate import Migrate, init, migrate, stamp, upgrade
import os

MIGRATIONS_FOLDER = "static/migrations"

migration = Migrate(app, db, render_as_batch=True)


# manager = Manager(app)
# manager.add_command('db', MigrateCommand)
def migrate_database():
    if not os.path.exists(MIGRATIONS_FOLDER):
        print(init(directory=MIGRATIONS_FOLDER))
    print("Stamp" + str(stamp(directory=MIGRATIONS_FOLDER, revision='head')))
    try:
        print(migrate(directory=MIGRATIONS_FOLDER))
    except:
        flash('Database could not be migrated!','danger')
    print(upgrade(directory=MIGRATIONS_FOLDER))

# if __name__ == '__main__':
#    manager.run()
