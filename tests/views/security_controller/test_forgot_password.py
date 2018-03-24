import pytest


@pytest.mark.usefixtures('user')
class TestForgotPassword:
    def test_email_required(self, client, templates):
        r = client.post('security.forgot_password')
        assert r.status_code == 200
        assert templates[0].template.name == 'security/forgot_password.html'
        assert 'Email not provided' in r.html

    def test_valid_email_required(self, client, templates):
        r = client.post('security.forgot_password',
                        data=dict(email='fail'))
        assert r.status_code == 200
        assert templates[0].template.name == 'security/forgot_password.html'
        assert 'Invalid email address' in r.html
        assert 'Specified user does not exist' in r.html

    def test_anonymous_user_required(self, client, templates):
        client.login_user()
        r = client.post('security.forgot_password')
        assert r.status_code == 302
        assert r.path == '/'
        r = client.follow_redirects(r)
        assert r.status_code == 200
        assert templates[0].template.name == 'site/index.html'

    def test_valid_request(self, user, client, outbox, templates):
        r = client.post('security.forgot_password',
                        data=dict(email=user.email))
        assert r.status_code == 200
        assert len(outbox) == 1
        assert templates[0].template.name == \
               'security/email/reset_instructions.html'
        assert templates[0].context.get('reset_link')

        assert templates[1].template.name == 'security/forgot_password.html'
        flash_msg = 'Instructions to reset your password have been sent to ' \
                    f'{user.email}'
        assert flash_msg in r.html
