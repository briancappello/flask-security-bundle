from flask_security import AnonymousUser, current_user


def test_get_logout(client, user):
    client.login_user()
    r = client.get('security.logout')
    assert r.status_code == 302
    assert r.path == '/'
    assert isinstance(current_user._get_current_object(), AnonymousUser)
