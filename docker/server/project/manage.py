
import os
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app.models import *
import datetime

app = create_app(os.getenv('APP_SETTINGS') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def runserver():
    app.run(debug=True, host='0.0.0.0')

@manager.command
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@manager.command
def setup_dev():
    setup_general()

def setup_general():
    """Runs the set-up needed for both local development and production.
       Also sets up first admin user."""
    Role.insert_roles()
    Condition.insert_data()
    admin_query = Role.query.filter_by(name='Administrator')
    if admin_query.first() is not None:
        if User.query.filter_by(email= "ardikabs@gmail.com").first() is None:
            import uuid
            generated_key = str(uuid.uuid4().hex)
            user = User(
                firstname='Ardika',
                lastname='Bagus',
                password= "rustygear125",
                registered_at= datetime.datetime.today(),
                email="ardikabs@gmail.com",
                identifier=str(uuid.uuid4()).split("-")[-1])
            db.session.add(user)
            db.session.commit()

            api_key = ApiKey(
                api_key=generated_key,
                user_id=user.id)
            db.session.add(api_key)
            db.session.commit()
            print('Added Administrator : {}'.format(user.fullname()))
            print('User identifier : {}'.format(user.identifier))
            print (api_key)

                


if __name__ == "__main__":
    manager.run()