import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('FLASK_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('FLASK_MAIL_PASSWORD')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_DEBUG = DEBUG
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/blog_dev'
    IP = '127.0.0.1'
    PORT = 5000
    APP_NAME = 'flask'
    HOST_NAME = 'localhost'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/blog_test'
    IP = '127.0.0.1'
    PORT = 5000
    APP_NAME = 'personal-site'
    HOST_NAME = 'localhost'


class ProductionConfig(Config):
    DEBUG = False
    MAIL_DEBUG = DEBUG
    PROPAGATE_EXCEPTIONS =False
    HOST_NAME = os.environ.get('OPENSHIFT_APP_DNS', 'localhost')
    APP_NAME = os.environ.get('OPENSHIFT_APP_NAME', 'personal-site')
    IP = os.environ.get('OPENSHIFT_PYTHON_IP', '127.0.0.1')
    PORT = int(os.environ.get('OPENSHIFT_PYTHON_PORT', 8080))
    SQLALCHEMY_DATABASE_URI = os.environ.get('OPENSHIFT_POSTGRESQL_DB_URL')


config = {"development": DevelopmentConfig,
          "testing": TestingConfig,
          "production": ProductionConfig,
          "default": DevelopmentConfig}
