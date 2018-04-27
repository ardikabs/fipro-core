

from flask import jsonify, render_template, abort
from . import main

@main.route('/')
def index():
    return render_template('main/index.html')

@main.route('/pages/typography')
def pages_typography():
    return render_template('main/typography.html')

@main.route('/pages/helper-classes')
def pages_helper_classes():
    return render_template('main/helper-classes.html')

@main.route('/coba')
def coba():
    if True:
        abort(404)
    return render_template('errors/404.html')