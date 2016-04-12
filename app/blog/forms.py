from flask.ext.wtf import Form
from wtforms import TextAreaField, TextField, BooleanField, SubmitField
from wtforms.validators import Required, ValidationError


class PostForm(Form):
    title = TextField("title", validators=[Required()])
    body = TextAreaField("body", validators=[Required()])
    is_published = BooleanField("publish", default=False)
    submit = SubmitField("save")


def validate_confirm(form, field):
    if field.data != "yes":
        raise ValidationError("Please enter 'yes'")


class DeleteForm(Form):
    confirm = TextField("confirm", validators=[validate_confirm])
    submit = SubmitField("delete")

