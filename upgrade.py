from data_Structure import app, db
# from flask_script import Manager

from flask import render_template, current_app, flash
from flask_migrate import Migrate, init, migrate, stamp, upgrade
from json import loads
import os

MIGRATIONS_FOLDER = "migrations/migrations/"
ADVANCED_FILE = "migrations.conf"

migration = Migrate(app, db, render_as_batch=True)


# manager = Manager(app)
# manager.add_command('db', MigrateCommand)
def migrate_database():
    check_special_commands()
    if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), MIGRATIONS_FOLDER)):
        init(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), MIGRATIONS_FOLDER))
    stamp(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), MIGRATIONS_FOLDER), revision='head')
    try:
        migrate(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), MIGRATIONS_FOLDER))
    except:
        print('Database could not be migrated!','danger')
    upgrade(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), MIGRATIONS_FOLDER))

def check_special_commands():
    if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), ADVANCED_FILE)):
        return
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ADVANCED_FILE), "r") as file:
            instr = file.readlines()
            res = db.session.execute("SELECT version_num from alembic_version")
            for row in res:
                print(row)
                ver = row["version_num"]
            for line in instr:
                if str(ver) in line:
                    db.session.execute(loads(line)["action"])
                    db.session.commit() 
    except Exception as e:
        print("Error // upgrade // {}".format(e))
        return
# if __name__ == '__main__':
#    manager.run()
