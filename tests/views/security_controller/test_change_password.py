import pytest

from flask_security import current_user


@pytest.mark.usefixtures('user')
class TestHtmlChangePassword:
    def test_auth_required(self, client):
        r = client.post('security.change_password')
        assert r.status_code == 401

    def test_fields_required(self, client, templates):
        client.login_user()
        r = client.post('security.change_password')
        assert r.status_code == 200
        assert templates[0].template.name == 'security/change_password.html'
        assert r.html.count('Password not provided') == 3

    def test_min_length(self, client, templates):
        client.login_user()
        r = client.post('security.change_password',
                        data=dict(password='password',
                                  new_password='fail',
                                  new_password_confirm='fail'))
        assert r.status_code == 200
        assert templates[0].template.name == 'security/change_password.html'
        assert 'Password must be at least 8 characters long.' in r.html

    def test_new_passwords_match(self, client, templates):
        client.login_user()
        r = client.post('security.change_password',
                        data=dict(password='password',
                                  new_password='long enough',
                                  new_password_confirm='but no match'))
        assert r.status_code == 200
        assert templates[0].template.name == 'security/change_password.html'
        assert 'Passwords do not match' in r.html

    def test_new_same_as_the_old(self, client, templates):
        client.login_user()
        r = client.post('security.change_password',
                        data=dict(password='password',
                                  new_password='password',
                                  new_password_confirm='password'))
        assert r.status_code == 200
        assert templates[0].template.name == 'security/change_password.html'
        assert 'Your new password must be different than your previous password' in r.html

    def test_valid_new_password(self, client, user):
        client.login_user()
        r = client.post('security.change_password',
                        data=dict(password='password',
                                  new_password='new password',
                                  new_password_confirm='new password'))
        assert r.status_code == 302
        assert r.path == '/'

        client.logout()
        client.login_with_creds(user.email, 'new password')
        assert current_user == user


@pytest.mark.usefixtures('user')
class TestApiChangePassword:
    def test_auth_required(self, api_client):
        r = api_client.post('security_api.change_password')
        assert r.status_code == 401

    def test_fields_required(self, api_client):
        api_client.login_user()
        r = api_client.post('security_api.change_password')
        assert r.status_code == 400, r.json
        assert 'password' in r.errors
        assert 'new_password' in r.errors
        assert 'new_password_confirm' in r.errors

    def test_min_length(self, api_client):
        api_client.login_user()
        r = api_client.post('security_api.change_password',
                            data=dict(password='password',
                                      new_password='fail',
                                      new_password_confirm='fail'))
        msg = 'Password must be at least 8 characters long.'
        assert msg in r.errors['new_password']

    def test_new_passwords_match(self, api_client):
        api_client.login_user()
        r = api_client.post('security_api.change_password',
                            data=dict(password='password',
                                      new_password='long enough',
                                      new_password_confirm='but no match'))
        assert 'new_password_confirm' in r.errors
        assert 'Passwords do not match' in r.errors['new_password_confirm']

    def test_new_same_as_the_old(self, api_client):
        api_client.login_user()
        r = api_client.post('security_api.change_password',
                            data=dict(password='password',
                                      new_password='password',
                                      new_password_confirm='password'))
        msg = 'Your new password must be different than your previous password.'
        assert msg in r.errors['new_password']

    def test_valid_new_password(self, api_client, user):
        api_client.login_user()
        r = api_client.post('security_api.change_password',
                            data=dict(password='password',
                                      new_password='new password',
                                      new_password_confirm='new password'))
        assert r.status_code == 200
        assert 'token' in r.json

        api_client.logout()
        api_client.login_with_creds(user.email, 'new password')
        assert current_user == user
