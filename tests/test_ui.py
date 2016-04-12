import logging
import time
import threading
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from app import create_app, init_db
from app.models import db, User, Post


class UITestCase(unittest.TestCase):

    _base_url = 'http://localhost:5000/'

    @classmethod
    def setUpClass(cls):
        # create application and client
        cls.client = webdriver.Chrome()
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        # supress logging to keep output clean
        logger = logging.getLogger('werkzeug')
        logger.setLevel("ERROR")

        # set up database and a user
        init_db()
        u = User(nickname="admin", email="ad@min.com", password="1234")
        db.session.add(u)
        db.session.commit()

        threading.Thread(target=cls.app.run).start()

    @classmethod
    def tearDownClass(cls):
        cls.client.get('http://localhost:5000/shutdown')
        cls.client.close()
        cls.app_context.pop()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def login(self, nickname="admin", password="1234"):
        self.client.get(self._base_url+'login')
        self.client.find_element_by_name("nickname").send_keys(nickname)
        self.client.find_element_by_name("password").send_keys(password)
        self.client.find_element_by_name("submit").send_keys(Keys.RETURN)
        time.sleep(0.5)

    def create_post(self, title, body, publish):
        self.login()
        self.client.get(self._base_url+'blog/new')
        self.client.find_element_by_name("title").send_keys(title)
        self.client.find_element_by_name("body").send_keys(body)
        self.client.find_element_by_name("body").send_keys(Keys.TAB)
        if publish:
            time.sleep(0.1)
            self.client.find_element_by_id("is_published").send_keys(Keys.SPACE)
        self.client.find_element_by_name("submit").send_keys(Keys.RETURN)
        time.sleep(0.1)

    def test_home_page_title(self):
        self.client.get(self._base_url)
        self.assertIn("Welcome!", self.client.title)

    def test_login_logout(self):
        self.login()

        # check for a flashed message saying we are logged in
        msg = self.client.find_element_by_id("flashes").text.lower()
        self.assertIn("logged in", msg)

        # try to logout
        self.client.find_element_by_tag_name("nav").click()
        time.sleep(0.1)
        self.client.find_element_by_link_text("LOGOUT").click()
        time.sleep(0.5)
        msg = self.client.find_element_by_id("flashes").text.lower()
        self.assertIn("logged out", msg)

    def test_wrong_password(self):
        self.login("admin", "123")
        msg = self.client.find_element_by_id("flashes").text.lower()
        self.assertIn("invalid password", msg)

    def test_wrong_username(self):
        self.login("adman", "1234")
        msg = self.client.find_element_by_id("flashes").text.lower()
        self.assertIn("invalid username", msg)

    def test_create_new_post(self):
        self.create_post("AN AUTOMATED POST!", "Isn't technology great???", True)
        self.assertIn("AN AUTOMATED POST!",
                      self.client.find_element_by_tag_name('h2').text)
        body = (self.client.find_element_by_id("wrapper")
                           .find_element_by_class_name("wrapper").text)
        self.assertIn("Isn't technology great?", body)

    def test_delete_post(self):
        self.create_post("to delete", "We are going to delete this post", True)
        self.client.find_element_by_link_text("Delete").click()
        self.client.find_element_by_name("confirm").send_keys("yes")
        self.client.find_element_by_name("submit").click()
        time.sleep(0.1)
        self.client.get(self._base_url+'blog/to-delete')
        text = self.client.find_element_by_tag_name("h1").text
        self.assertIn("not found", text.lower())

    def test_delete_confirm(self):
        self.create_post("not to delete", "We are not going to delete this post", True)
        self.client.find_element_by_link_text("Delete").click()
        self.client.find_element_by_name("confirm").send_keys("asdada")
        self.client.find_element_by_name("submit").click()
        time.sleep(0.1)
        text = self.client.find_element_by_class_name("errors").text
        self.assertIn("please enter 'yes'", text.lower())
