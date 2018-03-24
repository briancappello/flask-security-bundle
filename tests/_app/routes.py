from flask_controller_bundle import controller
from flask_security_bundle import SecurityController

from .views import SiteController


routes = [
    controller('/', SecurityController),
    controller('/', SiteController),
]
