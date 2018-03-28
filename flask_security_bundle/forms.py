from flask_security import current_user
from flask_security.forms import (
    ChangePasswordForm as BaseChangePasswordForm,
    ConfirmRegisterForm as BaseConfirmRegisterForm,
    EqualTo,
    ForgotPasswordForm,
    Form as BaseForm,
    Length,
    LoginForm,
    NextFormMixin,
    PasswordlessLoginForm,
    RegisterForm as BaseRegisterForm,
    ResetPasswordForm as BaseResetPasswordForm,
    SendConfirmationForm,
    get_form_field_label,
    password_required,
)
from flask_security.utils import get_message, verify_and_update_password
from wtforms import fields


password_length = Length(min=8, max=255,
                         message='Password must be at least 8 characters long.')


class PasswordFormMixin:
    password = fields.PasswordField(
        get_form_field_label('password'),
        validators=[password_required, password_length]
    )


class PasswordConfirmFormMixin:
    password_confirm = fields.PasswordField(
        get_form_field_label('retype_password'),
        validators=[EqualTo('password', message='RETYPE_PASSWORD_MISMATCH'),
                    password_required])


class ChangePasswordForm(PasswordFormMixin, BaseForm):
    new_password = fields.PasswordField(
        get_form_field_label('new_password'),
        validators=[password_required, password_length]
    )

    new_password_confirm = fields.PasswordField(
        get_form_field_label('retype_password'),
        validators=[EqualTo('new_password', message='RETYPE_PASSWORD_MISMATCH'),
                    password_required]
    )

    submit = fields.SubmitField(get_form_field_label('change_password'))

    def validate(self):
        if not super(ChangePasswordForm, self).validate():
            return False

        if not verify_and_update_password(self.password.data, current_user):
            self.password.errors.append(get_message('INVALID_PASSWORD')[0])
            return False
        if self.password.data == self.new_password.data:
            self.new_password.errors.append(
                get_message('PASSWORD_IS_THE_SAME')[0])
            return False
        return True


class ConfirmRegisterForm(PasswordFormMixin, BaseConfirmRegisterForm):
    pass


class RegisterForm(PasswordFormMixin, PasswordConfirmFormMixin,
                   BaseRegisterForm):
    pass


class ResetPasswordForm(PasswordFormMixin, PasswordConfirmFormMixin,
                        BaseResetPasswordForm):
    pass
