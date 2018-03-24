from flask_controller_bundle import Controller, route


class SiteController(Controller):
    @route('/')
    def index(self):
        return self.render('index')
