import re

from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_searchable import  SearchQueryMixin, make_searchable
from sqlalchemy_utils.types import TSVectorType

from . import login_manager


db = SQLAlchemy()
make_searchable()


class User(UserMixin, db.Model):
    def __repr__(self):
        return "<User %r>" % self.nickname

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(32), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError("Password is not readable.")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class PostQuery(BaseQuery, SearchQueryMixin):
    pass


class Post(db.Model):
    def __repr__(self):
        return "<Post %r>" % self.title

    query_class = PostQuery

    id = db.Column(db.Integer, primary_key=True)
    _title = db.Column('title', db.UnicodeText)
    slug = db.Column(db.UnicodeText)
    body = db.Column(db.UnicodeText)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_published = db.Column(db.Boolean)
    search_vector = db.Column(TSVectorType('title', 'body'))

    @hybrid_property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title
        self.slug = re.sub('[^\w]+', '-', self.title.lower())

    @hybrid_method
    def summary(self, n_words):
        # stripped = re.sub(r'[#>*-]', ' ', self.body)
        # return ' '.join(stripped.split()[:n_words]) + '...'
        stripped = self.body.split('.')
        return '. '.join(stripped[:n_words]) + ' ...'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
