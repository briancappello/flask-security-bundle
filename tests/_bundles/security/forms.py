from flask_security_bundle.forms import RegisterForm as BaseRegisterForm
from wtforms import fields


class RegisterForm(BaseRegisterForm):
    username = fields.StringField('Username')
    first_name = fields.StringField('First Name')
    last_name = fields.StringField('Last Name')
