import click

from flask.cli import cli, with_appcontext


@cli.group()
def users():
    """user commands"""


@users.command('list')
@with_appcontext
def list_users():
    """list users"""


@users.command('new')
@click.argument('query', nargs=1)
@with_appcontext
def new_user(query):
    """add new user"""
    kwargs = _query_to_dict(query)
    click.echo(str(kwargs))


@users.command('delete')
@click.argument('query', nargs=1)
@with_appcontext
def delete_user(query):
    """delete user"""
    kwargs = _query_to_dict(query)


@users.command('set-password')
@click.argument('query', nargs=1)
@with_appcontext
def set_password(query):
    """set a user's password"""
    kwargs = _query_to_dict(query)


@users.command('toggle-active')
@click.argument('query', nargs=1)
@with_appcontext
def toggle_active(query):
    """toggle whether or not a user is active"""
    kwargs = _query_to_dict(query)


@users.command('add-role')
@click.option('--user')
@click.option('--role')
@with_appcontext
def add_role(user, role):
    """add a role to a user"""
    user_kwargs = _query_to_dict(user)
    role_kwargs = _query_to_dict(role)


@users.command('remove-role')
@click.option('--user')
@click.option('--role')
@with_appcontext
def remove_role(user, role):
    """remove a role from a user"""
    user_kwargs = _query_to_dict(user)
    role_kwargs = _query_to_dict(role)


@cli.group()
def roles():
    """role commands"""


@roles.command()
@click.argument('name')
def new_role(name):
    """add new role"""


def _query_to_dict(query):
    return dict(map(str.strip, pair.split('=')) for pair in query.split(','))
