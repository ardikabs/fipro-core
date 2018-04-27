

from flask import jsonify, render_template
from . import accounts

@accounts.route('/login')
def login():
    return render_template('accounts/login.html')

@accounts.route('/manage')
def manage():
    return render_template('accounts/manage.html')

@accounts.route('/logout')
def logout():
    return render_template('accounts/login.html')
