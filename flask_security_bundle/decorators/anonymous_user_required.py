from flask import abort, flash, redirect, request
from flask_security import current_user
from flask_security.utils import get_post_action_redirect
from functools import wraps
from http import HTTPStatus


def anonymous_user_required(*decorator_args,
                            msg=None, category=None, redirect_url=None):
    """Decorator requiring no user be logged in

    Aborts with HTTP 403: Forbidden if there is an authenticated user
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            if current_user.is_authenticated:
                if request.is_json:
                    abort(HTTPStatus.FORBIDDEN)
                else:
                    if msg:
                        flash(msg, category)
                    return redirect(get_post_action_redirect(
                        'SECURITY_POST_LOGIN_VIEW', redirect_url))
            return fn(*args, **kwargs)
        return decorated

    if decorator_args and callable(decorator_args[0]):
        return wrapper(decorator_args[0])
    return wrapper
