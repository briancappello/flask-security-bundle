import pytest

from flask import url_for
from flask_security import current_user, AnonymousUser


@pytest.mark.usefixtures('user')
class TestResetPassword:
    def test_anonymous_user_required(self, user, client, security_service,
                                     password_resets):
        security_service.send_reset_password_instructions(user)
        token = password_resets[0]['token']
        client.login_user()
        r = client.get(url_for('security.reset_password', token=token))
        assert r.status_code == 302
        assert r.path == '/'

    @pytest.mark.options(SECURITY_RESET_PASSWORD_WITHIN='-1 seconds')
    def test_token_expired(self, user, client, security_service,
                           password_resets, outbox, templates):
        security_service.send_reset_password_instructions(user)
        assert len(password_resets) == 1
        token = password_resets[0]['token']

        r = client.get(url_for('security.reset_password', token=token))
        assert r.status_code == 302
        assert r.path == url_for('security.forgot_password')

        assert len(outbox) == 2
        # first email is for the valid reset request
        assert templates[0].template.name == 'security/email/reset_instructions.html'
        assert templates[0].context.get('reset_link')
        # second email is with a new token
        assert templates[1].template.name == 'security/email/reset_instructions.html'
        assert templates[1].context.get('reset_link')
        assert templates[0].context.get('reset_link') != templates[1].context.get('reset_link')

        # make sure the user is notified of the new email
        r = client.follow_redirects(r)
        assert r.status_code == 200
        assert templates[2].template.name == 'security/forgot_password.html'
        error_msg = 'You did not reset your password within -1 seconds. ' \
                    f'New instructions have been sent to {user.email}'
        assert error_msg in r.html

    def test_token_invalid(self, client, templates):
        r = client.get(url_for('security.reset_password', token='fail'))
        assert r.status_code == 302
        assert r.path == url_for('security.forgot_password')
        r = client.follow_redirects(r)
        assert r.status_code == 200
        assert templates[0].template.name == 'security/forgot_password.html'
        assert 'Invalid reset password token' in r.html

    def test_submit_errors(self, user, client, security_service, templates,
                           password_resets):
        security_service.send_reset_password_instructions(user)
        token = password_resets[0]['token']

        r = client.post(url_for('security.reset_password', token=token))
        assert r.status_code == 200
        assert templates[1].template.name == 'security/reset_password.html'
        assert r.html.count('Password not provided') == 2

        r = client.post(url_for('security.reset_password', token=token),
                            data=dict(password='short',
                                      password_confirm='short'))
        assert r.status_code == 200
        assert 'Password must be at least 6 characters' in r.html

        r = client.post(url_for('security.reset_password', token=token),
                        data=dict(password='long enough',
                                  password_confirm='but not the same'))
        assert r.status_code == 200
        assert 'Passwords do not match' in r.html

    def test_valid_submit(self, user, client, security_service,
                          password_resets, outbox, templates):
        security_service.send_reset_password_instructions(user)
        token = password_resets[0]['token']

        r = client.post(url_for('security.reset_password', token=token),
                        data=dict(password='new password',
                                  password_confirm='new password'))
        assert r.status_code == 302
        assert r.path == '/'
        # user should be logged in
        assert current_user == user

        assert len(outbox) == len(templates) == 2
        # first email is for the valid reset request
        assert templates[0].template.name == 'security/email/reset_instructions.html'
        assert templates[0].context.get('reset_link')
        # second email is to notify of the changed password
        assert templates[1].template.name == 'security/email/reset_notice.html'

        # make sure the password got updated in the database
        client.logout()
        assert isinstance(current_user._get_current_object(), AnonymousUser)
        client.login_with_creds(user.email, 'new password')
        assert current_user == user
