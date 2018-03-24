import pytest

from collections import namedtuple
from flask import template_rendered
from flask_mail_bundle import mail
from flask_security.signals import (
    reset_password_instructions_sent,
    user_confirmed,
    user_registered,
)
from flask_sqlalchemy_bundle import db as db_ext
from flask_unchained import TEST, AppFactory, unchained

from ._client import (
    ApiTestClient,
    ApiTestResponse,
    HtmlTestClient,
    HtmlTestResponse,
)

from ._model_fixtures import *


@pytest.fixture(autouse=True, scope='session')
def app():
    app = AppFactory.create_app(TEST)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


@pytest.yield_fixture
def client(app):
    app.response_class = HtmlTestResponse
    app.test_client_class = HtmlTestClient
    with app.test_client() as client:
        yield client


@pytest.yield_fixture
def api_client(app):
    app.response_class = ApiTestResponse
    app.test_client_class = ApiTestClient
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True, scope='session')
def db():
    db_ext.create_all()
    yield db_ext
    db_ext.drop_all()


@pytest.fixture(autouse=True)
def db_session(db):
    connection = db.engine.connect()
    transaction = connection.begin()
    session = db.create_scoped_session(options=dict(bind=connection, binds={}))
    db.session = session
    try:
        yield session
    finally:
        transaction.rollback()
        connection.close()
        session.remove()


@pytest.fixture()
def templates(app):
    records = []
    RenderedTemplate = namedtuple('RenderedTemplate', 'template context')

    def record(sender, template, context, **extra):
        records.append(RenderedTemplate(template, context))
    template_rendered.connect(record, app)

    try:
        yield records
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture()
def outbox():
    with mail.record_messages() as messages:
        yield messages


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


@pytest.fixture()
def security_service():
    return unchained.services.security_service


@pytest.fixture()
def user_manager():
    return unchained.services.user_manager
