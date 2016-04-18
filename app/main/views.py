from flask import current_app, flash, render_template, request
from flask.ext.mail import Message
from sqlalchemy import desc

from . import main
from .. import mail
from .forms import ContactForm
from ..models import Post


@main.route('/', methods=['GET', 'POST'])
def index():
    posts = (Post.query
                 .filter_by(is_published=True)
                 .order_by(desc(Post.timestamp))
                 .paginate(1, 4)
                 .items)
    form = ContactForm()

    if request.method == 'POST':
        if not form.validate():
            # flash("There was an error, please check the input")
            return render_template("index.html", posts=posts, form=form)
        else:
            msg = Message("Contact from site", sender=form.email.data,
                          recipients=[current_app.config['MAIL_USERNAME']])
            msg.body = """
            From: %s <%s>
            %s
            """ % (form.name.data, form.email.data, form.message.data)
            mail.send(msg)
            form = ContactForm()
            form.message.data = "Message Sent, Thank you!"
            return render_template("index.html", posts=posts, form=form)

    elif request.method == 'GET':
        return render_template("index.html", posts=posts, form=form)


@main.route('/demo')
def demo():
    return render_template("demo.html")


@main.route('/shutdown')
def server_shutdown():
    """ View to shutdown the server when in testing mode """
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return "Shutting down..."
