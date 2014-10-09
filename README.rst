flask-login-openerp
===================

OpenERP Login for Flask using Flask-Login

.. code-block:: python

    from flask import Flask
    from flask.ext.openerp import OpenERP
    from flask.ext.login import login_required
    from flask.ext.login_openerp import OpenERPLogin



    class AppConfig(object):
        OPENERP_PROTOCOL = 'xmlrpc'
        OPENERP_HOSTNAME = 'localhost'
        OPENERP_DATABASE = 'openerp'
        OPENERP_DEFAULT_USER = 'admin'
        OPENERP_DEFAULT_PASSWORD = 'admin'
        OPENERP_PORT = 8069
        SECRET_KEY = '9eaf50f88abcc3228ca55641bb97f5fc'


    app = Flask(__name__)
    app.config.from_object(AppConfig)
    OpenERP(app)
    login_manager = OpenERPLogin()
    login_manager.init_app(app)
    login_manager.logout_redirect_view = "index"

    @app.route('/')
    def index():
        return "Index!"

    @app.route('/secret')
    @login_required
    def secret():
        return "This is a secret"


    if __name__ == '__main__':
        app.run()

