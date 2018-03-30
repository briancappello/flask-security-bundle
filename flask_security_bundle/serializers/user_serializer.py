from flask_api_bundle import ma
from flask_unchained import injectable

from ..services import UserManager


class UserSerializer(ma.ModelSerializer):
    email = ma.Email(required=True)
    roles = ma.Nested('RoleSerializer', only='name', many=True)

    class Meta:
        model = 'User'
        exclude = ('confirmed_at', 'created_at', 'updated_at', 'user_roles')
        dump_only = ('active', 'roles')
        load_only = ('password',)

    def __init__(self, *args, user_manager: UserManager = injectable, **kwargs):
        self.user_manager = user_manager
        super().__init__(*args, **kwargs)

    @ma.validates('email')
    def validate_email(self, email):
        existing = self.user_manager.get_by(email=email)
        if existing and (self.is_create() or existing != self.instance):
            raise ma.ValidationError('Sorry, that email is already taken.')

    @ma.validates('password')
    def validate_password(self, value):
        min_len = 8
        if not value or len(value) < min_len:
            msg = f'Password must be at least {min_len} characters long.'
            raise ma.ValidationError(msg)
