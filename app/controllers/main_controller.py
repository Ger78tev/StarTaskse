# [file name]: main_controller.py
# [nuevo archivo]
from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/acerca')
def acerca():
    return render_template('acerca.html')

@main_bp.route('/contacto')
def contacto():
    return render_template('contacto.html')