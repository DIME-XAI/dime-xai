from flask import Blueprint

blueprint = Blueprint(
    'dime_blueprint',
    __name__,
    url_prefix='/api/dime',
    static_folder='static',
    template_folder='templates',
)
