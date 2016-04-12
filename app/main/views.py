from flask import current_app, render_template, request
from sqlalchemy import desc

from . import main
from ..models import Post


@main.route('/')
def index():
    posts = (Post.query
                 .filter_by(is_published=True)
                 .order_by(desc(Post.timestamp))
                 .paginate(1, 4)
                 .items)
    return render_template("index.html", posts=posts)


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
