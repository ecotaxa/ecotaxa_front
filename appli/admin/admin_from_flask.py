from flask_admin import base, Admin

from appli import app as main_app
from .views.users import UsersView

flaskAdmin = Admin(app=main_app,
                   name='Ecotaxa Administration',
                   # index_view=MyHomeView(),
                   base_template="admin2/base_no_link.html",
                   template_mode="bootstrap2")

# Add flask-admin related view
flaskAdmin.add_view(UsersView())

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
