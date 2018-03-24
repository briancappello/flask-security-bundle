import factory
import pytest

from datetime import datetime, timezone
from flask_sqlalchemy_bundle import db

from tests._bundles.security.models import User, Role, UserRole


class ModelFactory(factory.Factory):
    class Meta:
        abstract = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # query for existing by attrs on model_class with simple type values
        filter_kwargs = {k: v for k, v in kwargs.items()
                         if '__' not in k
                         and (v is None
                              or isinstance(v, (bool, int, str, float)))}
        instance = (model_class.query.filter_by(**filter_kwargs).one_or_none()
                    if filter_kwargs else None)

        if not instance:
            instance = model_class(*args, **kwargs)
            db.session.add(instance)
            db.session.commit()
        return instance


class UserFactory(ModelFactory):
    class Meta:
        model = User

    email = 'user@example.com'
    password = 'password'
    active = True
    confirmed_at = datetime.now(timezone.utc)


class RoleFactory(ModelFactory):
    class Meta:
        model = Role

    name = 'ROLE_USER'


class UserRoleFactory(ModelFactory):
    class Meta:
        model = UserRole

    user = factory.SubFactory(UserFactory)
    role = factory.SubFactory(RoleFactory)


class UserWithRoleFactory(UserFactory):
    user_role = factory.RelatedFactory(UserRoleFactory, 'user')


class UserWithTwoRolesFactory(UserFactory):
    _user_role = factory.RelatedFactory(UserRoleFactory, 'user',
                                        role__name='ROLE_USER')
    user_role = factory.RelatedFactory(UserRoleFactory, 'user',
                                       role__name='ROLE_USER1')


@pytest.fixture()
def user(request):
    kwargs = getattr(request.keywords.get('user'), 'kwargs', {})
    return UserWithTwoRolesFactory(**kwargs)


@pytest.fixture()
def role(request):
    kwargs = getattr(request.keywords.get('role'), 'kwargs', {})
    return RoleFactory(**kwargs)


@pytest.fixture()
def admin(request):
    kwargs = getattr(request.keywords.get('admin'), 'kwargs', {})
    kwargs = dict(**kwargs, email='admin@example.com',
                  _user_role__role__name='ROLE_ADMIN')
    kwargs.setdefault('user_role__role__name', 'ROLE_USER')
    return UserWithTwoRolesFactory(**kwargs)
