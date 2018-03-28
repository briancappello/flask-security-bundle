from flask_security.utils import (
    get_hmac, use_double_hash, _pwd_context)

from flask_unchained import unchained, injectable


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
        verified = _pwd_context.verify(get_hmac(password), user.password)
    else:
        # Try with original password.
        verified = _pwd_context.verify(password, user.password)

    if verified and _pwd_context.needs_update(user.password):
        user.password = password
        user_manager.save(user)
    return verified
