from flask_admin import base, Admin

from appli import app as main_app
# We cannot avoid to know the application DB...
from appli.database import db as ecotaxa_db
# Create admin
from .admin_views import UsersView, UsersViewRestricted, ProjectsViewLight, ProjectsView, ObjectsView, \
    ObjectsFieldsView, SamplesView, ProcessView, AcquisitionsView

# class MyHomeView(AdminIndexView):
#     @expose('/')
#     def index(self):
#         arg1 = 'Hello'
#         return self.render('index_with_others.html', arg1=arg1)
#

flaskAdmin = Admin(app=main_app,
                   name='Ecotaxa Administration',
                   # index_view=MyHomeView(),
                   base_template="admin2/base_no_link.html",
                   template_mode="bootstrap2")

# Add flask-admin related views
flaskAdmin.add_view(UsersView(ecotaxa_db.session, name="Users"))
flaskAdmin.add_view(UsersViewRestricted(ecotaxa_db.session, name="users", endpoint="userrest"))

flaskAdmin.add_view(ProjectsViewLight(ecotaxa_db.session, endpoint="projectlight", category='Projects'))
flaskAdmin.add_view(ProjectsView(ecotaxa_db.session, name="Projects (Full)", category='Projects'))
flaskAdmin.add_view(ObjectsView(ecotaxa_db.session, category='Objects'))
flaskAdmin.add_view(ObjectsFieldsView(ecotaxa_db.session, category='Objects'))
flaskAdmin.add_view(SamplesView(ecotaxa_db.session, category='Objects'))
flaskAdmin.add_view(ProcessView(ecotaxa_db.session, category='Objects'))
flaskAdmin.add_view(AcquisitionsView(ecotaxa_db.session, category='Objects'))

# Add links to the blueprint-managed entry points
flaskAdmin.add_link(base.MenuLink('Ecotaxa Home', url='/'))

flaskAdmin.add_link(base.MenuLink('View DB Size (admin only)',
                                  category='Database', url='/admin/db/viewsizes'))
flaskAdmin.add_link(base.MenuLink('View DB Bloat (admin only)',
                                  category='Database', url='/admin/db/viewbloat'))
flaskAdmin.add_link(base.MenuLink('SQL Console (admin only)',
                                  category='Database', url='/admin/db/console'))
flaskAdmin.add_link(base.MenuLink('Recompute Projects and Taxo stat (can be long)(admin only)',
                                  category='Database', url='/admin/db/recomputestat'))
