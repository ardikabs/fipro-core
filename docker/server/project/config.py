
import os
import sys
import requests
basedir = os.path.abspath(os.path.dirname(__file__))

''' Environment Variable Configuration '''
if os.path.exists('.env'):
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]           

class Config:
    APP_NAME = os.environ.get('APP_NAME') or 'Server-Side Web App'
    SERVER_IP = requests.get('http://httpbin.org/ip').json().get('origin')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    
    MONGO_URI = "mongodb://mongodb:27017/fipro"

    CELERY_BROKER_URL= 'redis://redis:6379/0'
    CELERY_RESULT_BACKEND= 'redis://redis:6379/0'
    
    
    if os.environ.get('SECRET_KEY'):
        SECRET_KEY = os.environ.get('SECRET_KEY')
    else:
        SECRET_KEY = 'SECRET_KEY_ENV_VAR_NOT_SET'
        print('SECRET KEY ENV VAR NOT SET! SHOULD NOT SEE IN PRODUCTION')
        
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    ASSETS_DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

    @classmethod
    def init_app(cls, app):
        print ("RUNNING ON DEBUG MODE")


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

    @classmethod
    def init_app(cls, app):
        print ("RUNNING ON TESTING MODE")



config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}