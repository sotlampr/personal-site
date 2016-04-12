from datetime import datetime

import unittest
from flask import current_app
from app import create_app, init_db

from sqlalchemy_searchable import search

from app.models import db, User, Post


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # initialize database and add a user
        init_db()
        u = User(nickname="admin", email="ad@min.com", password="1234")
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        self.app_context.pop()

    def add_post(self):
        user = User.query.filter_by(nickname="admin").first()
        post = Post(title="This is a post",
                    body="Testing and writing and drinking "
                    "add some more please until we are "
                    "good to go", timestamp=datetime.utcnow(),
                    user_id=user.id, is_published=True)
        db.session.add(post)

        post = Post(title="A Hidden post",
                    body="Contents undisclosed",
                    timestamp=datetime.utcnow(),
                    user_id=user.id, is_published=False)
        db.session.add(post)
        db.session.commit()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_views(self):
        views = {'main_index': '/',
                 'blog_index': '/blog',
                 'blog_archive': '/blog/archive',
                 'projects': '/projects',
                 'login': '/login'}
        for name, view in views.items():
            response = self.client.get(view, follow_redirects=True)
            self.assertEqual(response.status_code, 200,
                             msg="view %s failed" % name)

    def test_user_correct_pass(self):
        user = User.query.filter_by(nickname="admin").first()
        self.assertTrue(user.verify_password("1234"))

    def test_user_wrong_pass(self):
        user = User.query.filter_by(nickname="admin").first()
        self.assertFalse(user.verify_password("123"))

    def test_user_add(self):
        user = User(nickname="user", email="us@er.com", password="4321")
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            self.fail("Adding user to database raised exception")
            raise e

        retrieved_user = db.session.query(User).filter_by(nickname="user").first()
        self.assertEqual(user.email, retrieved_user.email)
        self.assertEqual(2, retrieved_user.id)

    def test_post_add(self):
        user = User.query.filter_by(nickname="admin").first()
        post = Post(title="This is a post",
                    body="Testing and writing and drinking "
                         "add some more please until we are "
                         "good to go",
                    timestamp=datetime.utcnow(), user_id=user.id)
        try:
            db.session.add(post)
            db.session.commit()
        except Exception as e:
            self.fail("Adding post to database raised exception")
            raise e

        retrieved_post = db.session.query(Post).filter_by(id=1).first()
        self.assertEqual(post.slug, retrieved_post.slug)

    def test_post_search(self):
        self.add_post()

        for word in ("test", "drinking", "drink", "please", "good"):
            query = search(db.session.query(Post), word)
            retrieved_post = query.first()
            self.assertIsNotNone(retrieved_post,
                                 msg="when testing for %s" % word)

    def test_post_view(self):
        self.add_post()
        response = self.client.get('/blog/this-is-a-post', follow_redirects=True)
        self.assertIn(b"This is a post", response.data)

    def test_forbidden_views(self):
        self.add_post()
        views = {"unpublished posts page": "/blog/unpublished",
                 "new post": "/blog/new",
                 "unpublished post": "/blog/a-hidden-post",
                 "edit post": "/blog/this-is-a-post/edit",
                 "logout": "/logout"}
        for name, view in views.items():
            response = self.client.get(view, follow_redirects=True)
            self.assertEqual(response.status_code, 401,
                             msg="Access shouldn't be allowed "
                                 "for %s" % name)
