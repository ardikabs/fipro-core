
import os
from flask_script import Manager, Shell
from app import create_app, db
from app.models import Role, User, Agent, Sensor, ApiKey
import datetime

app = create_app(os.getenv('APP_SETTINGS') or 'default')
manager = Manager(app)

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
    admin_query = Role.query.filter_by(name='Administrator')
    if admin_query.first() is not None:
        if User.query.filter_by(email= "admin@fipro.com").first() is None:
            import uuid
            key = str(uuid.uuid4().hex)
            user = User(
                firstname='Admin',
                lastname='Fipro',
                password= "admin",
                registered_at= datetime.datetime.today(),
                email="admin@fipro.com",
                identifier=str(uuid.uuid4()).split("-")[-1])
            db.session.add(user)
            db.session.commit()

            apikey = ApiKey(
                apikey=key,
                user_id=user.id)
            db.session.add(apikey)
            db.session.commit()
            print('Added Administrator : {}'.format(user.fullname()))
            print('User identifier : {}'.format(user.identifier))
            print (apikey)

                


if __name__ == "__main__":
    manager.run()