from flask_sqlalchemy.model import Model

from app import app, db, dao
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from app.models import User, Airport, Airplane, UserRole
from flask_login import current_user, logout_user
from flask import redirect

admin = Admin(app=app, name="Flight Admin", template_mode="bootstrap4")

class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

class AirportView(AdminView):
    column_list = ['code','name','city','country']

class AirplaneView(AdminView):
    column_list = ['name']


class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

class StatsView(AuthenticatedView):
    @expose('/')
    def index(self):
        stats = dao.get_revenue_stats()
        return self.render('admin/stats.html', stats=stats)

admin.add_view(AdminView(User, db.session))
admin.add_view(AirportView(Airport, db.session))
admin.add_view(AirplaneView(Airplane, db.session))
admin.add_view(StatsView(name='Statical'))
admin.add_view(LogoutView(name='Logout'))