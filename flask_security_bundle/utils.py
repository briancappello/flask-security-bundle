import base64
import hashlib
import hmac

from flask_login.utils import _get_user
from flask_unchained import current_app, unchained, injectable
from werkzeug.local import LocalProxy

current_user = LocalProxy(lambda: _get_user())
_security = LocalProxy(lambda: current_app.extensions['security'])


def encode_string(string):
    """Encodes a string to bytes, if it isn't already.

    :param string: The string to encode"""

    if isinstance(string, str):
        string = string.encode('utf-8')
    return string


def get_hmac(password):
    """Returns a Base64 encoded HMAC+SHA512 of the password signed with
    the salt specified by ``SECURITY_PASSWORD_SALT``.

    :param password: The password to sign
    """
    salt = current_app.config.get('SECURITY_PASSWORD_SALT')

    if salt is None:
        raise RuntimeError(
            'The configuration value `SECURITY_PASSWORD_SALT` must '
            'not be None when the value of `SECURITY_PASSWORD_HASH` is '
            'set to "%s"' % _security.password_hash)

    h = hmac.new(encode_string(salt), encode_string(password), hashlib.sha512)
    return base64.b64encode(h.digest())


def get_auth_token(user):
    """Returns the user's authentication token."""
    data = [str(user.id),
            _security.hashing_context.hash(encode_string(user._password))]
    return _security.remember_token_serializer.dumps(data)


# overridden to not call hash_password or depend on the datastore
@unchained.inject('user_manager')
def verify_and_update_password(password, user, user_manager=injectable):
    """Returns ``True`` if the password is valid for the specified user.

    Additionally, the hashed password in the database is updated if the
    hashing algorithm happens to have changed.

    :param password: A plaintext password to verify
    :param user: The user to verify against
    """
    if use_double_hash(user.password):
        verified = _security.pwd_context.verify(get_hmac(password), user.password)
    else:
        # Try with original password.
        verified = _security.pwd_context.verify(password, user.password)

    if verified and _security.pwd_context.needs_update(user.password):
        user.password = password
        user_manager.save(user)
    return verified


def hash_password(password):
    """Hash the specified plaintext password.

    It uses the configured hashing options.

    .. versionadded:: 2.0.2

    :param password: The plaintext password to hash
    """
    if use_double_hash():
        password = get_hmac(password).decode('ascii')

    return _security.pwd_context.hash(
        password,
        **current_app.config.get('SECURITY_PASSWORD_HASH_OPTIONS', {}).get(
            current_app.config.get('SECURITY_PASSWORD_HASH'), {}))


def use_double_hash(password_hash=None):
    """Return a bool indicating whether a password should be hashed twice."""
    single_hash = current_app.config.get('SECURITY_PASSWORD_SINGLE_HASH')
    if single_hash and _security.password_salt:
        raise RuntimeError('You may not specify a salt with '
                           'SECURITY_PASSWORD_SINGLE_HASH')

    if password_hash is None:
        is_plaintext = _security.password_hash == 'plaintext'
    else:
        is_plaintext = _security.pwd_context.identify(password_hash) == 'plaintext'

    return not (is_plaintext or single_hash)
