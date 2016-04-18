from flask import Flask
from flask.ext.login import LoginManager
from flask_wtf.csrf import CsrfProtect
from flask.ext.migrate import Migrate
from flask.ext.mail import Mail
from flaskext.markdown import Markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from sqlalchemy_searchable import make_searchable

from config import config

login_manager = LoginManager()
csrf = CsrfProtect()
migrate = Migrate()
mail = Mail()

from app.models import db
from app.filters import timesince_filter

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # blueprints
    from app.main import main as main_blueprint
    from app.blog import blog as blog_blueprint
    from app.admin import admin as admin_blueprint
    from app.projects import projects as projects_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(blog_blueprint, url_prefix='/blog')
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(projects_blueprint, url_prefix='/projects')

    # initializations
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    md = Markdown(app)
    md.register_extension(CodeHiliteExtension)

    app.jinja_env.filters['timesince'] = timesince_filter

    return app


def init_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
