import pytest

from flask_security import current_user


class TestLogin:
    def test_get_login(self, client, templates):
        r = client.get('security.login')
        assert r.status_code == 200
        assert templates[0].template.name == 'security/login.html'

    def test_login_errors(self, client, templates):
        r = client.post('security.login')
        assert templates[0].template.name == 'security/login.html'
        assert 'Email not provided' in r.html
        assert 'Password not provided' in r.html

    @pytest.mark.options(SECURITY_USER_IDENTITY_ATTRIBUTES=['email'])
    def test_login_with_email(self, client, user):
        r = client.post('security.login', data=dict(email=user.email,
                                                    password='password'))
        assert r.status_code == 302
        assert r.path == '/'
        assert current_user == user

    @pytest.mark.user(active=False)
    def test_active_user_required(self, client, templates, user):
        r = client.post('security.login', data=dict(email=user.email,
                                                    password='password'))
        assert r.status_code == 200
        assert templates[0].template.name == 'security/login.html'
        assert 'Account is disabled' in r.html
