

from flask import jsonify, render_template
from . import deploy

@deploy.route('/')
def index():
    return jsonify({
        "message":"Hello Deploy"
    })