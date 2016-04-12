from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required


class LoginForm(Form):
    nickname = StringField("nickname", validators=[Required()])
    password = PasswordField("password", validators=[Required()])
    remember_me = BooleanField("stay logged in", default=True)
    submit = SubmitField("Submit")
