

from flask import jsonify, render_template
from . import main

@main.route('/')
def index():
    return jsonify({
        "message":"Hello World"
    })