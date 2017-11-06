# app/home/views.py


from flask import abort, render_template
from flask_login import current_user, login_required
from . import home
from . machine_info import machine_stats
db_file = '/home/pi/prj/scripts/chalice/raspieye/instance/app.sqlite'

@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """
    return render_template('home/index.html', title="Welcome")

@home.route('/dashboard')
@login_required
def dashboard():
    """
    Render the dashboard template on the /dashboard route
    """

    return render_template('home/dashboard.html', title="Dashboard")

@home.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # prevent non-admins from accessing the page
    if not current_user.is_admin:
        abort(403)
    load, title_list = machine_stats.cpu_snapshot()
    directories = ['/']
    disks, directories = machine_stats.df_space(directories)
    table_stats, data_systems = machine_stats.db_health(db_file)

    return render_template('home/admin_dashboard.html', title="Dashboard", load=load, disks=disks, title_list=title_list,    directories=directories, data_systems=data_systems)
