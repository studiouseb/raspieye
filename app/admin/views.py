# app/admin/views.py

from flask import abort, flash, redirect, render_template, url_for, request, send_from_directory, jsonify
from flask_login import current_user, login_required

import os

from ..tscripts.image_search.colordescriptor import ColorDescriptor
from ..tscripts.image_search.searcher import Searcher

import os
from . import admin
from . forms import DepartmentForm, EmployeeAssignForm, RoleForm, PhotoUploadForm
from ..models import Department, Employee, Role, Upload
from .. import db
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
APP_ROUTE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(os.path.dirname(__file__), 'index.csv')
print(APP_ROUTE)

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

    GEN_images = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set/uploads/')
    DS_images = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set/doc_scanner/')
    MTC_images = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set/measures/')
    SC_images = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set/Search_Candidates/')

    if form.validate_on_submit():

        if form.folder_name.data == 'Gen':
            path = GEN_images
            path_load = 'Gen'
        elif form.folder_name.data == 'DS':
            path = DS_images
            path_load = 'DS'
        elif form.folder_name.data == 'MTC':
            path = MTC_images
            path_load = 'MTC'
        elif form.folder_name.data == 'SC':
            path = SC_images
            path_load = 'SC'
        if allowed_file(form.photo.data.filename):

            try:
                # add upload to the database
                file_name=form.photo.data.filename
                file_data=form.photo.data
                upload = Upload(file_name=file_name,
                                  description=form.description.data,
                                  path=path)
                db.session.add(upload)
                db.session.commit()
                filename = secure_filename(form.photo.data.filename)

                save_path = path
                form.photo.data.save(os.path.join(save_path, filename))
                flash('You have successfully added a new file.')
                return render_template("admin/folder_gallery/completed.html", filename = file_name, path_load = path_load)

            except:
                # in case upload name already exists
                db.session.rollback()
                flash('Error: That file name already exists. Duplicates are discouraged.')
                return render_template('admin/folder_gallery/upload.html', form = form)

        else:
            flash('That is not a supported file type.')
            return render_template('admin/folder_gallery/upload.html', form = form)

    else:
        flash('Please complete the form. COMPLETE.')
        return render_template('admin/folder_gallery/upload.html', form = form)





@admin.route('<path>/<filename>')
def send_image(path,filename):
    path = path
    GEN_images = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set/uploads/')
    DS_images = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set/doc_scanner/')
    MTC_images = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set/measures/')
    SC_images = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set/Search_Candidates/')
    if path == 'Gen':
        path = GEN_images
    elif path == 'DS':
        path = DS_images
    elif path == 'MTC':
        path = MTC_images
    elif path == 'SC':
        path = SC_images
    return send_from_directory(path,filename)


@admin.route('/folder_gallery/<path>', methods=['GET', 'POST'])
@login_required
def display_folder(path):
    """
    Select the folder to display in gallery
    """
    check_admin()
    input_path = path
    image_files = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set')
    GEN_images = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set/uploads')
    DS_images = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set/doc_scanner')
    MTC_images = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set/measures')
    SC_images = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set/Search_Candidates')
    SB_images = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set/Search_Holidaysnaps')

    if check_first_gallery():

        all_images = [image_files, GEN_images, DS_images, MTC_images, SB_images, SC_images]
        #print(folder_name)
        for path_ in all_images:
            print(path_)
            image_names = os.listdir(path_)
            a = Upload.query.filter(Upload.file_name.in_(image_names)).all()

            for img in image_names:
                try:
                    to_be_uploaded = Upload(file_name=img, description='script generated', path=path_)
                    db.session.add(to_be_uploaded)
                    db.session.commit()
                except:
                    pass

        GEN_images = os.path.join(APP_ROUTE[:-5],'static/img/unified_image_set/uploads/')
        image_names = os.listdir(GEN_images)
        image_names.sort()
        return render_template('admin/folder_gallery/folder_gallery.html', image_names=image_names, path=imput_path)

    else:
        if input_path == 'Gen':
            input_path = GEN_images
            path_load = 'Gen'
        elif input_path == 'MTC':
            input_path = MTC_images
            path_load = 'MTC'
        elif input_path == 'SC':
            input_path = SC_images
            path_load = 'SC'
        elif input_path == 'DS':
            input_path = DS_images
            path_load = 'DS'

        image_names = os.listdir(input_path)
        image_names.sort()

        return render_template('admin/folder_gallery/folder_gallery.html', image_names=image_names, path=path_load)

@admin.route('/image_search', methods=['GET', 'POST'])
def image_search():
    if request.method == "POST":

        RESULTS_ARRAY = []

        # get url
        image_url = request.form.get('img')

        try:

            # initialize the image descriptor
            cd = ColorDescriptor((8, 12, 3))

            # load the query image and describe it
            from skimage import io
            import cv2
            query = io.imread(image_url)
            query = (query * 255).astype("uint8")
            (r, g, b) = cv2.split(query)
            query = cv2.merge([b, g, r])
            features = cd.describe(query)

            # perform the search
            searcher = Searcher(INDEX)
            results = searcher.search(features)

            # loop over the results, displaying the score and image name
            for (score, resultID) in results:
                RESULTS_ARRAY.append(
                    {"image": str(resultID), "score": str(score)})

            # return success
            return jsonify(results=(RESULTS_ARRAY[:3]))

        except:

            # return error
            jsonify({"sorry": "Sorry, no results! Please try again."}), 500


@admin.route('/measure', methods=['GET', 'POST'])
def measure():
    return helloagain
