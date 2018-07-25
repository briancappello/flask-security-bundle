import re

from flask_unchained.bundles.api import ma
from flask_security_bundle.serializers import (
    UserSerializer as BaseUserSerializer)


NON_ALPHANUMERIC_RE = re.compile(r'[^\w]')


class UserSerializer(BaseUserSerializer):
    @ma.validates('username')
    def validate_username(self, username):
        if re.search(NON_ALPHANUMERIC_RE, username):
            raise ma.ValidationError('Usernames can only contain letters, '
                                     'numbers, and/or underscore characters.')

        existing = self.user_manager.get_by(username=username)
        if existing and (self.is_create() or existing != self.instance):
            raise ma.ValidationError('Sorry, that username is already taken.')
