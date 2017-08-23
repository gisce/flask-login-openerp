from flask import (
    Blueprint, render_template, flash, redirect, url_for, request, g,
    session
)
from flask_wtf import Form
from wtforms import validators, StringField, PasswordField
from flask_login import (
    LoginManager, UserMixin, login_user, login_required, logout_user
)
from flask_erppeek import get_object


class OpenERPUser(UserMixin):
    def is_authenticated(self):
        return True


class LoginForm(Form):
    login = StringField('Username', validators=[validators.required()])
    password = PasswordField('Password', validators=[validators.required()])


class OpenERPLogin(LoginManager):

    def __init__(self, app=None, add_context_processor=True):
        super(OpenERPLogin,
              self).__init__(app, add_context_processor=add_context_processor)
        self.user_loader(self.load_user)
        self.login_view = "openerp_login.login"
        self.logout_redirect_view = None
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
            user_id = obj.search([('id', '=', user_id)])
            if user_id:
                user_id = user_id[0]
                user = OpenERPUser()
                user.id = user_id
                return user
            else:
                return None
        except Exception:
            return None

    @login_required
    def logout(self):
        logout_user()
        if 'openerp_user_id' in session:
            del session['openerp_user_id']
        if 'openerp_password' in session:
            del session['openerp_password']
        flash("You have been logout", "info")
        if self.logout_redirect_view:
            return redirect(url_for(self.logout_redirect_view))
        return "Log out!"

    def login(self):
        obj = get_object('res.users')
        user_name = g.openerp_cnx.user
        user_id = obj.search([('login', '=', user_name)])
        logo = obj.browse(user_id[0]).company_id.logo

        if self.login_form:
            form = self.login_form
        else:
            form = LoginForm()
        if form.validate_on_submit():
            user_id = obj.search([
                ('login', '=', form.login.data),
                ('password', '=', form.password.data)
            ])
            if user_id:
                user_id = user_id[0]
                flash("Login successful", "success")
                user = OpenERPUser()
                user.id = user_id
                login_user(user)
                session['openerp_user_id'] = user_id
                session['openerp_password'] = form.password.data
                return redirect(request.args.get("next") or url_for('index'))
            else:
                flash("User or password incorrect.", "danger")
        return render_template("openerp_login/login.html", form=form, logo=logo)
