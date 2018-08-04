import sys

from flask_unchained import unchained
from flask_unchained.cli import cli, click
from flask_unchained.commands.utils import print_table

from .extensions import Security
from .services import UserManager, RoleManager, SecurityService

security: Security = unchained.extensions.security
security_service: SecurityService = unchained.services.security_service
user_manager: UserManager = unchained.services.user_manager
role_manager: RoleManager = unchained.services.role_manager


@cli.group()
def users():
    """
    User model commands.
    """


@users.command('list')
def list_users():
    """
    List users.
    """
    print_table(
        ['ID', 'First Name', 'Last Name', 'Email', 'Active', 'Confirmed At'],
        [(user.id,
          user.first_name,
          user.last_name,
          user.email,
          'True' if user.active else 'False',
          user.confirmed_at.strftime('%Y-%m-%d %H:%M%z') if user.confirmed_at else 'None',
          ) for user in user_manager.find_all()])


@users.command('create')
@click.option('--email', prompt='Email address',
              help="The user's email address")
@click.option('--password', prompt='Password',
              hide_input=True, confirmation_prompt=True)
@click.option('--active/--inactive', prompt='Should user be active?',
              help='Whether or not the new user should be active.',
              default=False, show_default=True)
@click.option('--confirmed-at', prompt='Confirmed at timestamp (or enter "now")',
              default=None, show_default=True)
def create_user(email, password, active, confirmed_at):
    """
    Create a new user.
    """
    if confirmed_at == 'now':
        confirmed_at = security.datetime_factory()
    user = user_manager.create(email=email, password=password, active=active,
                               confirmed_at=confirmed_at)
    if click.confirm('Are you sure you want to create {user!r}?'):
        user_manager.save(user, commit=True)
        click.echo(f'Successfully created a new user: {user!r}')
    else:
        click.echo('Cancelled')


@users.command('delete')
@click.argument('query', nargs=1, help='The query to search for a user by. For example, '
                                       '`id=5`, `email=a@a.com` or '
                                       '`first_name=A,last_name=B`.')
def delete_user(query):
    """
    Delete a user.
    """
    user = _query_to_user(query)
    if click.confirm(f'Are you sure you want to delete {user!r}?'):
        user_manager.delete(user, commit=True)
        click.echo(f'Successfully deleted: {user!r}')
    else:
        click.echo('Cancelled.')


@users.command('set-password')
@click.argument('query', help='The query to search for a user by. For example, `id=5`, '
                              '`email=a@a.com` or `first_name=A,last_name=B`.')
@click.option('--password', prompt='Password',
              hide_input=True, confirmation_prompt=True)
@click.option('--send-email/--no-email', default=False,
              help='Whether or not to send the user a notification email.')
def set_password(query, password, send_email):
    """
    Set a user's password.
    """
    user = _query_to_user(query)
    if click.confirm(f'Are you sure you want to change {user!r}\'s password?'):
        security_service.change_password(user, password, send_email=send_email)
        user_manager.save(user, commit=True)
        click.echo(f'Successfully updated password for {user!r}')
    else:
        click.echo('Cancelled.')


@users.command('confirm')
@click.argument('query', nargs=1, help='The query to search for a user by. For example, '
                                       '`id=5`, `email=a@a.com` or '
                                       '`first_name=A,last_name=B`.')
def confirm_user(query):
    """
    Confirm a user account.
    """
    user = _query_to_user(query)
    if click.confirm(f'Are you sure you want to confirm {user!r}?'):
        if security_service.confirm_user(user):
            click.echo(f'Successfully confirmed {user!r} at '
                       f'{user.confirmed_at.strftime("%Y-%m-%d %H:%M:%S.%f%z")}')
            user_manager.save(user, commit=True)
        else:
            click.echo(f'{user!r} has already been confirmed.')
    else:
        click.echo('Cancelled')


@users.command('activate')
@click.argument('query', nargs=1, help='The query to search for a user by. For example, '
                                       '`id=5`, `email=a@a.com` or '
                                       '`first_name=A,last_name=B`.')
def activate_user(query):
    """
    Activate a user.
    """
    user = _query_to_user(query)
    if click.confirm(f'Are you sure you want to activate {user!r}?'):
        user.active = True
        user_manager.save(user, commit=True)
        click.echo(f'Successfully activated {user!r}')
    else:
        click.echo('Cancelled.')


@users.command('deactivate')
@click.argument('query', nargs=1, help='The query to search for a user by. For example, '
                                       '`id=5`, `email=a@a.com` or '
                                       '`first_name=A,last_name=B`.')
def deactivate_user(query):
    """
    Deactivate a user.
    """
    user = _query_to_user(query)
    if click.confirm(f'Are you sure you want to deactivate {user!r}?'):
        user.active = False
        user_manager.save(user, commit=True)
        click.echo(f'Successfully deactivated {user!r}')
    else:
        click.echo('Cancelled')


@users.command('add-role')
@click.option('-u', '--user', help='The query to search for a user by. For example, '
                                   '`id=5`, `email=a@a.com` or '
                                   '`first_name=A,last_name=B`.')
@click.option('-r', '--role', help='The query to search for a role by. For example, '
                                   '`id=5` or `name=ROLE_USER`.')
def add_role(user, role):
    """
    Add a role to a user.
    """
    user = _query_to_user(user)
    role = _query_to_role(role)
    if click.confirm(f'Are you sure you want to add {role!r} to {user!r}?'):
        user.roles.append(role)
        user_manager.save(user, commit=True)
        click.echo(f'Successfully added {role!r} to {user!r}')
    else:
        click.echo('Cancelled')


@users.command('remove-role')
@click.option('-u', '--user', help='The query to search for a user by. For example, '
                                   '`id=5`, `email=a@a.com` or '
                                   '`first_name=A,last_name=B`.')
@click.option('-r', '--role', help='The query to search for a role by. For example, '
                                   '`id=5` or `name=ROLE_USER`.')
def remove_role(user, role):
    """
    Remove a role from a user.
    """
    user = _query_to_user(user)
    role = _query_to_role(role)
    if click.confirm(f'Are you sure you want to remove {role!r} from {user!r}?'):
        user.roles.remove(role)
        user_manager.save(user, commit=True)
        click.echo(f'Successfully removed {role!r} from {user!r}')
    else:
        click.echo('Cancelled')


@cli.group()
def roles():
    """
    Role commands.
    """


@roles.command(name='list')
def list_roles():
    """
    List roles.
    """
    print_table(['ID', 'Name'],
                [(role.id, role.name) for role in role_manager.find_all()])


@roles.command(name='create')
@click.option('--name', prompt='Role name',
              help='The name of the role to create, eg `ROLE_USER`.')
def create_role(name):
    """
    Create a new role.
    """
    role = role_manager.create(name=name)
    if click.confirm('Are you sure you want to create {role!r}?'):
        role_manager.save(role, commit=True)
        click.echo(f'Successfully created a new role: {role!r}')
    else:
        click.echo('Cancelled')


@roles.command(name='delete')
@click.argument('query', help='The query to search for a role by. For example, '
                              '`id=5` or `name=ROLE_USER`.')
def delete_role(query):
    """
    Delete a role.
    """
    role = _query_to_role(query)
    if click.confirm('Are you sure you want to delete {role!r}?'):
        role_manager.delete(role, commit=True)
        click.echo(f'Successfully deleted: {role!r}')
    else:
        click.echo('Cancelled.')


def _query_to_user(query):
    kwargs = _query_to_kwargs(query)
    user = user_manager.get_by(**kwargs)
    if not user:
        click.secho(f'ERROR: Could not locate a user by {_format_query(query)}',
                    fg='white', bg='red')
        sys.exit(1)
    return user


def _query_to_role(query):
    kwargs = _query_to_kwargs(query)
    role = role_manager.get_by(**kwargs)
    if not role:
        click.secho(f'ERROR: Could not locate a role by {_format_query(query)}',
                    fg='white', bg='red')
        sys.exit(1)
    return role


def _query_to_kwargs(query):
    return dict(map(str.strip, pair.split('=')) for pair in query.split(','))


def _format_query(query):
    return ', '.join([f'{k!s}={v!r}'
                      for k, v in _query_to_kwargs(query).items()])
