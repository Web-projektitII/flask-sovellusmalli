import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = os.environ.get('MAILTRAP_MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAILTRAP_MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAILTRAP_MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAILTRAP_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAILTRAP_MAIL_PASSWORD')
    FS_MAIL_SUBJECT_PREFIX = '[Flaskprojekti]'
    FS_MAIL_SENDER = 'Flaskprojekti Admin <flaskprojekti@example.com>'
    FS_ADMIN = os.environ.get('FS_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FS_POSTS_PER_PAGE = 25

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class LocalConfig(Config):
    DEBUG = True
    DB_USERNAME = os.environ.get('LOCAL_DB_USERNAME')
    DB_PASSWORD = os.environ.get('LOCAL_DB_PASSWORD')
    DB_NAME = os.environ.get('LOCAL_DB_NAME')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@localhost:3306/' + DB_NAME
    # SQLALCHEMY_ECHO = True (dokumentaatio)
    SQLALCHEMY_ECHO = "debug"
    # WTF_CSRF_ENABLED = False

class HerokuConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('CLEARDB_DATABASE_URL')
    SQLALCHEMY_ECHO = "debug"
    MAIL_SERVER = os.environ.get('SENDGRID_MAIL_SERVER', 'smtp.sendgrid.net')
    MAIL_PORT = int(os.environ.get('SENDGRID_MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('SENDGRID_MAIL_USE_TLS', 'true')
    # MAIL_USE_SSL = os.environ.get('MAILTRAP_MAIL_USE_SSL', 'false')   
    MAIL_USERNAME = os.environ.get('SENDGRID_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('SENDGRID_MAIL_PASSWORD')
    FS_MAIL_SENDER = 'wohjelmointi@gmail.com'
    # WTF_CSRF_ENABLED = False    

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'local': LocalConfig,
    'heroku': HerokuConfig,

    'default': DevelopmentConfig
}
