from flask.ext.wtf import Form
from wtforms import TextAreaField, TextField, SubmitField
from wtforms.validators import Required, Email


class ContactForm(Form):
    name = TextField("name", [Required()])
    email = TextField("email", [Required(), Email()])
    message = TextAreaField("message", [Required()])
    sumbit = SubmitField("send")
