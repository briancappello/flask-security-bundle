import json
import pytest

from flask_api_bundle.pytest import ApiTestResponse
from flask_controller_bundle.pytest import (
    HtmlTestClient, HtmlTestResponse, _process_test_client_args)
from flask_security.signals import (
    reset_password_instructions_sent,
    user_confirmed,
    user_registered,
)

class SecurityTestClient(HtmlTestClient):
    token = None

    def login_user(self):
        return self.login_with_creds('user@example.com', 'password')

    def login_admin(self):
        return self.login_with_creds('admin@example.com', 'password')

    def login_as(self, user):
        self.token = user.get_auth_token()
        return self.get('security.check_auth_token')

    def login_with_creds(self, email, password):
        return super().open('security.login', method='POST',
                            data=dict(email=email, password=password))

    def logout(self):
        self.token = None
        self.get('security.logout')

    def open(self, *args, **kwargs):
        args, kwargs = _process_test_client_args(args, kwargs)
        kwargs.setdefault('headers', {})
        if self.token:
            kwargs['headers']['Authentication-Token'] = self.token
        return super().open(*args, **kwargs)

    def follow_redirects(self, response):
        return super().open(response.location, follow_redirects=True)


class SecurityApiTestClient(SecurityTestClient):
    def open(self, *args, **kwargs):
        kwargs['data'] = json.dumps(kwargs.get('data'))

        kwargs.setdefault('headers', {})
        kwargs['headers']['Content-Type'] = 'application/json'
        kwargs['headers']['Accept'] = 'application/json'

        return super().open(*args, **kwargs)


@pytest.fixture()
def client(app):
    app.test_client_class = SecurityTestClient
    app.response_class = HtmlTestResponse
    with app.test_client() as client:
        yield client


@pytest.fixture()
def api_client(app):
    app.test_client_class = SecurityApiTestClient
    app.response_class = ApiTestResponse
    with app.test_client() as client:
        yield client


@pytest.fixture()
def registrations(app):
    records = []

    def record(sender, *args, **kwargs):
        records.append(kwargs)
    user_registered.connect(record, app)

    try:
        yield records
    finally:
        user_registered.disconnect(record, app)


@pytest.fixture()
def confirmations(app):
    records = []

    def record(sender, *args, **kwargs):
        records.append(kwargs['user'])
    user_confirmed.connect(record, app)

    try:
        yield records
    finally:
        user_confirmed.disconnect(record, app)


@pytest.fixture()
def password_resets(app):
    records = []

    def record(sender, *args, **kwargs):
        records.append(kwargs)
    reset_password_instructions_sent.connect(record, app)

    try:
        yield records
    finally:
        reset_password_instructions_sent.disconnect(record, app)
