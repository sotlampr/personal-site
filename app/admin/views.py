from flask import redirect, request, render_template, url_for, flash
from flask.ext.login import login_user, logout_user, login_required

from . import admin
from .forms import LoginForm
from ..models import User


@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.nickname.data).first()
        if user:
            if user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                flash("Succesfully logged in!")
                return redirect(url_for('blog.index'))
            else:
                flash("Invalid password.")
        else:
            flash("Invalid username.")
    return render_template('admin/login.html', form=form)


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('admin.login'))
