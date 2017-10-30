# app/admin/views.py

from flask import abort, flash, redirect, render_template, url_for, request, send_from_directory
from flask_login import current_user, login_required
import os
from . import admin
from . forms import DepartmentForm, EmployeeAssignForm, RoleForm, PhotoUploadForm
from ..models import Department, Employee, Role, Upload
from .. import db
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
APP_ROUTE = os.path.dirname(os.path.abspath(__file__))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_first_gallery():
    """
    Check if user is first user in DB, if so make admin.
    """
    candidates = Upload.query.count()
    if candidates > 0:
        return False
    else:
        return True



def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)

# Department Views

@admin.route('/departments', methods=['GET', 'POST'])
@login_required
def list_departments():
    """
    List all departments
    """
    check_admin()

    departments = Department.query.all()

    return render_template('admin/departments/departments.html',
                           departments=departments, title="Departments")

@admin.route('/departments/add', methods=['GET', 'POST'])
@login_required
def add_department():
    """
    Add a department to the database
    """
    check_admin()

    add_department = True

    form = DepartmentForm()
    if form.validate_on_submit():
        department = Department(name=form.name.data,
                                description=form.description.data)
        try:
            # add department to the database
            db.session.add(department)
            db.session.commit()
            flash('You have successfully added a new department.')
        except:
            # in case department name already exists
            flash('Error: department name already exists.')

        # redirect to departments page
        return redirect(url_for('admin.list_departments'))

    # load department template
    return render_template('admin/departments/department.html', action="Add",
                           add_department=add_department, form=form,
                           title="Add Department")

@admin.route('/departments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_department(id):
    """
    Edit a department
    """
    check_admin()

    add_department = False

    department = Department.query.get_or_404(id)
    form = DepartmentForm(obj=department)
    if form.validate_on_submit():
        department.name = form.name.data
        department.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the department.')

        # redirect to the departments page
        return redirect(url_for('admin.list_departments'))

    form.description.data = department.description
    form.name.data = department.name
    return render_template('admin/departments/department.html', action="Edit",
                           add_department=add_department, form=form,
                           department=department, title="Edit Department")

@admin.route('/departments/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_department(id):
    """
    Delete a department from the database
    """
    check_admin()

    department = Department.query.get_or_404(id)
    db.session.delete(department)
    db.session.commit()
    flash('You have successfully deleted the department.')

    # redirect to the departments page
    return redirect(url_for('admin.list_departments'))

    return render_template(title="Delete Department")

@admin.route('/roles')
@login_required
def list_roles():
    check_admin()
    """
    List all roles
    """
    roles = Role.query.all()
    return render_template('admin/roles/roles.html',
                           roles=roles, title='Roles')

@admin.route('/roles/add', methods=['GET', 'POST'])
@login_required
def add_role():
    """
    Add a role to the database
    """
    check_admin()

    add_role = True

    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data,
                    description=form.description.data)

        try:
            # add role to the database
            db.session.add(role)
            db.session.commit()
            flash('You have successfully added a new role.')
        except:
            # in case role name already exists
            flash('Error: role name already exists.')

        # redirect to the roles page
        return redirect(url_for('admin.list_roles'))

    # load role template
    return render_template('admin/roles/role.html', add_role=add_role,
                           form=form, title='Add Role')

@admin.route('/roles/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_role(id):
    """
    Edit a role
    """
    check_admin()

    add_role = False

    role = Role.query.get_or_404(id)
    form = RoleForm(obj=role)
    if form.validate_on_submit():
        role.name = form.name.data
        role.description = form.description.data
        db.session.add(role)
        db.session.commit()
        flash('You have successfully edited the role.')

        # redirect to the roles page
        return redirect(url_for('admin.list_roles'))

    form.description.data = role.description
    form.name.data = role.name
    return render_template('admin/roles/role.html', add_role=add_role,
                           form=form, title="Edit Role")

@admin.route('/roles/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_role(id):
    """
    Delete a role from the database
    """
    check_admin()

    role = Role.query.get_or_404(id)
    db.session.delete(role)
    db.session.commit()
    flash('You have successfully deleted the role.')

    # redirect to the roles page
    return redirect(url_for('admin.list_roles'))

    return render_template(title="Delete Role")

@admin.route('/employees')
@login_required
def list_employees():
    """
    List all employees
    """
    check_admin()

    employees = Employee.query.all()
    return render_template('admin/employees/employees.html',
                           employees=employees, title='Employees')

@admin.route('/employees/assign/<int:id>', methods=['GET', 'POST'])
@login_required
def assign_employee(id):
    """
    Assign a department and a role to an employee
    """
    check_admin()

    employee = Employee.query.get_or_404(id)

    # prevent admin from being assigned a department or role
    if employee.is_admin:
        abort(403)

    form = EmployeeAssignForm(obj=employee)
    if form.validate_on_submit():
        employee.department = form.department.data
        employee.role = form.role.data
        db.session.add(employee)
        db.session.commit()
        flash('You have successfully assigned a department and role.')

        # redirect to the roles page
        return redirect(url_for('admin.list_employees'))

    return render_template('admin/employees/employee.html',
                           employee=employee, form=form,
                           title='Assign Employee')

# select folder to view in gallery

@admin.route('/upload', methods=['GET', 'POST'])
@login_required
def select_file():
    """
    Select the folder to display in gallery
    """
    check_admin()
    add_upload = True
    form = PhotoUploadForm()
    if form.validate_on_submit():
        if allowed_file(form.photo.data.filename):
            file_name=form.photo.data.filename
            file_data=form.photo.data
            upload = Upload(file_name=file_name,
                              description=form.description.data)
            db.session.add(upload)
            db.session.commit()
        try:
            # add upload to the database
            filename = secure_filename(form.photo.data.filename)
            print(filename)
            save_path = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set/uploads/')
            form.photo.data.save(os.path.join(save_path, filename))
            flash('You have successfully added a new file.')
        except:
            # in case upload name already exists
            flash('Error: file name already exists.')

    else:
        return render_template('admin/folder_gallery/upload.html', form = form)


    return render_template("admin/folder_gallery/completed.html", filename=file_name)


@admin.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory('static/img/unified_image_set/uploads/', filename)


@admin.route('/folder_gallery', methods=['GET', 'POST'])
@login_required
def display_folder():
    """
    Select the folder to display in gallery
    """
    check_admin()

    folder_name = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set/uploads/')
    #print(folder_name)
    image_names = os.listdir(folder_name)
    registered_images = Upload.query.all()

    a = Upload.query.filter(Upload.file_name.in_(image_names)).all()

    print('next is a')
    print(a)
    if check_first_gallery():
        for i in image_names:
            if i in a:
                pass
            else:
                try:

                    to_be_uploaded = Upload(file_name=i, description='script generated')
                    db.session.add(to_be_uploaded)
                    db.session.commit()
                except:
                    pass

    print(registered_images)
    image_names.sort()
    #print(image_names)
    return render_template('admin/folder_gallery/folder_gallery.html', image_names=image_names)



''' def upload():
    print(APP_ROUTE)
    target = os.path.join(APP_ROUTE[:-5], 'static/img/unified_image_set/uploads/')
    print(target)
    if not os.path.isdir(target):
        print('target directory not found')

    for file in request.files.getlist("file"):

        filename = file.filename
        print("the filename is ", filename)
        destination = target + filename
        print('this is the destination', destination)
        file.save(destination)
        print('completed save')
    return render_template("admin/folder_gallery/completed.html", target=target, filename=filename)   '''
