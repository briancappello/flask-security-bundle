from flask_login.utils import _get_user
from flask_unchained import current_app
from werkzeug.local import LocalProxy

current_user = LocalProxy(lambda: _get_user())
_security = LocalProxy(lambda: current_app.extensions['security'])
