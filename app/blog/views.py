from datetime import datetime

from flask import abort, flash, request, render_template, redirect, url_for
from flask.ext.login import login_required, current_user
from sqlalchemy import desc

from . import blog
from .forms import PostForm, DeleteForm

from ..models import db, Post


@blog.route('/')
@blog.route('/index')
@blog.route('/page/<int:page>')
def index(page=1):
    posts = (Post.query
                 .filter_by(is_published=True)
                 .order_by(desc(Post.timestamp))
                 .paginate(page, 3))
    return render_template('blog/index.html', posts=posts)


@blog.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = PostForm(request.form)
    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data,
                    timestamp=datetime.utcnow(),
                    user_id=int(current_user.get_id()),
                    is_published=form.is_published.data)
        db.session.add(post)
        db.session.commit()
        if form.is_published.data:
            flash("Post is now published.")
        else:
            flash("Post updated")

        return redirect('blog/'+post.slug)

    return render_template('blog/edit.html', form=form)


@blog.route('/<slug>/')
def show_post(slug):
    post = Post.query.filter_by(slug=slug).first()
    if post is not None:
        if post.is_published:
            return render_template('blog/post.html', post=post)
        else:
            if  current_user.is_authenticated:
                flash("This post is unpublished.")
                return render_template('blog/post.html', post=post)
            else:
                abort(401)
    else:
        abort(404)


@blog.route('/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first()
    if post is not None:
        if request.method == 'GET':
            form = PostForm(obj=post)
            return render_template('blog/edit.html', form=form)
        else:
            form = PostForm(request.form)
            post.title = form.title.data
            post.body = form.body.data
            post.is_published = form.is_published.data
            post.user_id = current_user.get_id()
            db.session.commit()
            flash("Post updated.")
            return redirect(url_for('blog.show_post', slug=post.slug))
    else:
        abort(404)


@blog.route('/<slug>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(slug):
    form = DeleteForm(request.form)
    post = Post.query.filter_by(slug=slug).first()
    if post is not None:
        if form.validate_on_submit():
            db.session.delete(post)
            db.session.commit()
            return redirect(url_for('blog.index'))
        else:
            return render_template("blog/delete.html", form=form)
    else:
        abort(404)


"""
@blog.route('/search/<search_terms>/')
def search():
    return render_template('blog/search.html')
"""


@blog.route('/archive')
@blog.route('/archive/page/<int:page>')
def archive(page=1):
    posts = (Post.query
                 .filter_by(is_published=True)
                 .order_by(desc(Post.timestamp))
                 .paginate(page, 10))
    return render_template('blog/archive.html',
                           head_title="Blog Archive",
                           header_title="Archives",
                           posts=posts)


@blog.route('/unpublished')
@login_required
def show_unpublished():
    posts = (Post.query
                 .filter_by(is_published=False)
                 .order_by(desc(Post.timestamp))
                 .paginate(1, 10))
    return render_template('blog/archive.html',
                           head_title="Administration",
                           header_title="Unpublished posts",
                           posts=posts)
