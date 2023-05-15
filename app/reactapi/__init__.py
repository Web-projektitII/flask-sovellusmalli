from flask import Blueprint

reactapi = Blueprint('reactapi', __name__)

from . import views