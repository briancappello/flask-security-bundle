import pytest

from flask_security import current_user
from flask_security_bundle import SecurityService
from flask_sqlalchemy_bundle import SessionManager


class TestHtmlLogin:
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


@pytest.mark.usefixtures('user')
class TestApiLogin:
    def test_token_login(self, api_client, user):
        r = api_client.get(
            'security.check_auth_token',
            headers={'Authentication-Token': user.get_auth_token()})
        assert r.status_code == 200
        assert 'user' in r.json
        assert r.json['user']['id'] == user.id

    def test_json_login_errors(self, api_client):
        r = api_client.post('security_api.login',
                            data=dict(email=None, password=None))
        assert 'Invalid email and/or password.' == r.json['error']

    def test_json_login_with_email(self, api_client, user):
        r = api_client.post('security_api.login',
                            data=dict(email=user.email, password='password'))
        assert r.status_code == 200
        assert 'user' in r.json
        assert 'token' in r.json
        assert r.json['user']['id'] == user.id
        assert current_user == user

    def test_active_user_required(self, api_client, user,
                                  session_manager: SessionManager):
        user.active = False
        session_manager.add(user, commit=True)
        r = api_client.post('security_api.login',
                            data=dict(email=user.email, password='password'))
        assert r.status_code == 401

    @pytest.mark.user(confirmed_at=None)
    def test_confirmed_user_required(self, api_client, user,
                                     security_service: SecurityService,
                                     session_manager: SessionManager):
        security_service.register_user(user)
        session_manager.commit()

        r = api_client.post('security_api.login',
                            data=dict(email=user.email, password='password'))
        assert r.status_code == 401
        assert 'Email requires confirmation.' == r.json['error']
