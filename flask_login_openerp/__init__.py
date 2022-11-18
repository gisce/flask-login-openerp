from flask import (
    Blueprint, render_template, flash, redirect, url_for, request, g,
    session
)
from flask_wtf import FlaskForm
from wtforms import validators, StringField, PasswordField
from flask_login import (
    LoginManager, UserMixin, login_user, login_required, logout_user
)
from flask_erppeek import get_object


class OpenERPUser(UserMixin):
    def is_authenticated(self):
        if 'openerp_user_id' in session:
            return True
        else:
            return False


class LoginForm(FlaskForm):
    login = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])


class OpenERPLogin(LoginManager):

    def __init__(self, app=None, add_context_processor=True):
        super(OpenERPLogin,
              self).__init__(app, add_context_processor=add_context_processor)
        self.user_loader(self.load_user)
        self.login_view = "openerp_login.login"
        self.logout_redirect_view = None
        self.login_redirect_view = None
        self.blueprint = Blueprint('openerp_login', __name__,
                                   template_folder="templates")
        self.blueprint.add_url_rule('/login', 'login', self.login,
                                    methods=['GET', 'POST'])
        self.blueprint.add_url_rule('/logout', 'logout', self.logout)
        if app is not None:
            self.init_app(app, add_context_processor)

        self.login_message_category = "warning"
        self.login_form = None

    def init_app(self, app, add_context_processor=True):
        super(OpenERPLogin, self).init_app(app, add_context_processor)
        app.register_blueprint(self.blueprint)

    @staticmethod
    def load_user(user_id):
        try:
            user_id = int(user_id)
            obj = get_object('res.users')
            user_data = obj.read([('id', '=', user_id)], ["context_lang"])
            if user_id:
                user_id = user_data[0]["id"]
                user_lang = user_data[0]["context_lang"]
                user = OpenERPUser()
                user.id = user_id
                user.lang = user_lang
                return user
            else:
                return None
        except Exception:
            return None

    @login_required
    def logout(self):
        if '_flashes' in session:
            session['_flashes'] = []
        logout_user()
        if 'openerp_user_id' in session:
            del session['openerp_user_id']
            flash("You have been logout", "info")
        if 'openerp_password' in session:
            del session['openerp_password']
        if 'openerp_user' in session:
            del session['openerp_user']
        if self.logout_redirect_view:
            response = redirect(url_for(self.logout_redirect_view))
            response.headers['Cache-Control'] = ', '.join([
                'no-cache', 'no-store', 'must-revalidate'
            ])
            response.headers['Pragma'] = 'no-cache'
            response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
            return response
        return "Log out!"

    def login(self, template=None, values=None):
        """
        Resolves the login request
        :param template: name of template file to use as login page.
        :return:
        """
        if template is None:
            template = "openerp_login/login.html"
        if values is None:
            values = {}
        obj = get_object('res.users')
        user_name = g.openerp_cnx.user
        user_id = obj.search([('login', '=', user_name)])
        company = obj.browse(user_id[0]).company_id
        company_logo = company.logo
        company_name = company.name

        if self.login_form:
            form = self.login_form
        else:
            form = LoginForm()
        if form.validate_on_submit():
            try:
                g.openerp_cnx.login(form.login.data, form.password.data)
            except Exception:
                user_id = None

            if user_id:
                user_id = obj.search([('login', '=', form.login.data)])[0]
                flash("Login successful", "success")
                user = OpenERPUser()
                user.id = user_id
                login_user(user)
                session['openerp_user_id'] = user_id
                session['openerp_user'] = form.login.data
                session['openerp_password'] = form.password.data
                return redirect(
                    request.args.get("next")
                    or url_for(self.login_redirect_view)
                )
            else:
                flash("User or password incorrect.", "danger")
        return render_template(template,
                               form=form,
                               logo=company_logo,
                               company_name=company_name,
                               footer_text=values.get('footer_text',
                                                      'GISCE-TI - WebGIS'),
                               page_title=values.get('page_title', 'WebGIS'))
