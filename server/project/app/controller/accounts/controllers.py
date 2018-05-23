

from flask import (
    jsonify, 
    render_template,
    redirect,
    request,
    url_for,
    flash)

from flask_login import(
    current_user,
    login_required,
    login_user,
    logout_user
)

from app import db
from app.models import User
from app.controller.accounts.forms import(
    LoginForm
)

from . import accounts

@accounts.route('/login', methods=['GET','POST'])
def login():
    """Log in an existing user."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.password_hash is not None and \
                user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('You are now logged in. Welcome back {}'.format(user.fullname()), 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('Invalid email or password', 'form-error')
        render_template('accounts/login.html', form=form)
    return render_template('accounts/login.html', form=form)

@accounts.route('/manage')
def manage():
    return render_template('accounts/manage.html')


@accounts.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('accounts.login'))
