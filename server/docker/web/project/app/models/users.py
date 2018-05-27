
from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash
from app import db, login_manager
import datetime
class Permission:
    GENERAL = 0x01
    ADMINISTER = 0xff

class Role(db.Model):

    __tablename__ = "roles"
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(64), unique=True)
    index       = db.Column(db.String(64))
    default     = db.Column(db.Boolean, default=False, index=True)
    permission  = db.Column(db.Integer)
    users       = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.GENERAL, 'main', True),
            'Administrator': (
                Permission.ADMINISTER,
                'admin',
                False
            )
        }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            
            role.permission = roles[r][0]
            role.index      = roles[r][1]
            role.default    = roles[r][2]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role \'%s\'>' % self.name

class User(UserMixin, db.Model):
    
    __tablename__   = "users"
    id              = db.Column(db.Integer, primary_key=True)
    firstname       = db.Column(db.String(64), nullable=True, index=True)
    lastname        = db.Column(db.String(64), index=True)
    email           = db.Column(db.String(100), unique=True, index=True)
    password_hash   = db.Column(db.String(128))
    registered_at   = db.Column(db.DateTime)
    role_id         = db.Column(db.Integer, db.ForeignKey('roles.id'))
    agents          = db.relationship('Agent', backref='user', lazy='dynamic')
    apikey          = db.relationship('ApiKey', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == "admin@fipro.com":
                self.role = Role.query.filter_by(
                    permission = Permission.ADMINISTER).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()



    def fullname(self):
        return "%s %s" % (self.firstname, self.lastname)
    
    def get_apikey(self):
        return self.APIKey

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions
    
    def is_admin(self):
        return self.can(Permission.ADMINISTER)

    @property
    def password(self):
        raise AttributeError('Password is not readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def reset_password(self, token, new_password):
        """Verify the new password for this user."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

class ApiKey(db.Model):
    __tablename__ = 'apikey'
    id  = db.Column(db.Integer, primary_key=True)
    apikey = db.Column(db.String(64), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.datetime.today())

    def __str__(self):
        return "ApiKey: {}".format(self.apikey)
    
    def __repr__(self):
        return "<ApiKey of {}>".format(self.user.email)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))