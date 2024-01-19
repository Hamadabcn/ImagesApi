from flask import Blueprint

bp = Blueprint('actions', __name__, url_prefix='/actions')

@bp.route('/resize', methods=["POST"])
def resize():
    pass

@bp.route('/presets/<preset>', methods=["POST"])
def resize_preset(preset):
    pass

@bp.route('/rotate', methods=["POST"])
def rotate():
    pass

@bp.route('/flap', methods=["POST"])
def flap():
    pass