# app/admin/__init__.py

from flask import Blueprint

admin = Blueprint('raspi-eye', __name__)

from . import views
