import pytest


class TestRegister:
    def test_get(self, client, templates):
        r = client.get('security.register')
        assert r.status_code == 200
        assert templates[0].template.name == 'security/register.html'

    def test_errors(self, client, templates):
        r = client.post('security.register')
        assert r.status_code == 200
        assert templates[0].template.name == 'security/register.html'
        assert 'Email not provided' in r.html
        assert 'Password not provided' in r.html

    def test_register_confirmation_required(self, client, templates, outbox):
        r = client.post('security.register', data=dict(
            email='hello@example.com',
            password='password',
            password_confirm='password',
        ))
        assert r.status_code == 302
        assert r.path == '/'
        assert templates[0].template.name == 'security/email/welcome.html'
        assert outbox[0].recipients == ['hello@example.com']
        assert 'Please confirm your email' in outbox[0].html

    @pytest.mark.options(SECURITY_CONFIRMABLE=False)
    def test_register(self, client, templates, outbox):
        r = client.post('security.register', data=dict(
            email='hello@example.com',
            password='password',
            password_confirm='password',
        ))
        assert r.status_code == 302
        assert r.path == '/'
        assert templates[0].template.name == 'security/email/welcome.html'
        assert outbox[0].recipients == ['hello@example.com']
        assert 'You may now login at' in outbox[0].html
