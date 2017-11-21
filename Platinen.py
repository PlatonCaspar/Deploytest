import os
import time
import urllib
import tempfile

from markupsafe import Markup
from flask import render_template, request, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_login import login_user, logout_user, login_required, current_user
from flask_nav import register_renderer
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256
from werkzeug.utils import secure_filename
from werkzeug.datastructures import MultiDict
from upgrade import migrate_database


import addPlatineForm
import data_Structure
import delPlatineForm
import deleteUserForm
import nav
import ownNavRenderer
import project_forms
import registerUserForm
import searchForm
import view
import BOM_Converter
import search
from data_Structure import app, db
import board_labels
from historyForm import HistoryForm, EditHistoryForm

nav.login_manager.anonymous_user = data_Structure.User

RELATIVE_PICTURE_PATH = 'static/Pictures'
UPLOAD_FOLDER = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), RELATIVE_PICTURE_PATH)
DATA_FOLDER = os.path.dirname(os.path.abspath(__file__))

RELATIVE_DATA_UPLOAD_FOLDER = 'static/data_folder'
DATA_UPLOAD_FOLDER = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), RELATIVE_DATA_UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


# def set_logged_user(state):
#    logged_user = state



@app.template_filter('urlencode')
def urlencode_filter(s):
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    s = urllib.parse.quote(s)

    return Markup(s)


# data_Structure.db.create_all()
def is_logged_in():
    if session.get('logged_in'):
        return True
    else:
        return False


def delete_project():
    pass


def clean_exb_scan(exb_scan):
    exb_scan = exb_scan.split('@')
    exb_scan = exb_scan[1].split('P')[1]

    return exb_scan


@nav.login_manager.user_loader
def load_user(user_id):
    return data_Structure.User.get(user_id)


@app.route('/registerUser/', methods=['GET', 'POST'])
def register_user():
    nav.nav.register_element("frontend_top", view.nav_bar())
    user_to_register = registerUserForm.RegisterUser(request.form)
    if request.method == 'POST':
        if user_to_register.password.data == user_to_register.password_again.data:
            new_user = data_Structure.User(username=user_to_register.username.data,
                                           password=user_to_register.password.data,
                                           email=user_to_register.email_adress.data)

            if data_Structure.User.query.filter_by(username=new_user.username).all() != []:
                # check if user already exists
                flash('User does already exist!', 'danger')
                return render_template('registerUserForm.html', form=user_to_register,
                                       search_form=searchForm.SearchForm())
            if data_Structure.User.query.filter_by(email=new_user.email).all() != []:
                flash(
                    'There is already somone registered with the same Email adress!', 'danger')
                return redirect(url_for('register_user'))

            data_Structure.db.session.add(new_user)
            data_Structure.db.session.commit()
            if data_Structure.User.query.filter_by(email=new_user.email).scalar() is not None:
                # if Board is no longer not available
                flash('User was successfully added!', 'success')
                return render_template('registerUserForm.html', form=user_to_register,
                                       search_form=searchForm.SearchForm())
        else:
            flash('The Passwords do not match!', 'danger')
            return render_template('registerUserForm.html', form=user_to_register, search_form=searchForm.SearchForm())

    return render_template('registerUserForm.html', form=user_to_register, search_form=searchForm.SearchForm())


@app.route('/logout/')
@login_required
def logout():
    nav.nav.register_element("frontend_top", view.nav_bar())
    logout_user()
    view.logged_user = None
    flash('you were logged out successfully!', 'success')
    return redirect(url_for('start'))


@app.route('/login/', methods=['GET', 'POST'])
@app.route('/login/<last_page_1>/', methods=['GET', 'POST'])
def login(last_page_1=None):
    last_page = request.args.get('next')

    no_url_for = False
    url = None
    if last_page is None:
        last_page = last_page_1
        if last_page:
            last_page = last_page.replace('_', '/')  # [1:len(last_page) - 2]

    try:
        # print(last_page)
        url = url_for(last_page)
    except:
        no_url_for = True
        try:
            redirect(last_page)

        except:
            last_page = None
            url = None
            no_url_for = False
    url = last_page
    nav.nav.register_element("frontend_top", view.nav_bar())
    user_form = registerUserForm.LoginUser(request.form)
    if request.method == 'POST':
        if data_Structure.User.query.filter_by(
                username=user_form.username.data).scalar() is None:  # check if User exists
            flash('User does not exist!', 'danger')
            return render_template('loginUser.html', form=user_form, search_form=searchForm.SearchForm())
        login_to_user = data_Structure.User.query.filter_by(
            username=user_form.username.data).first()
        if pbkdf2_sha256.verify(user_form.password.data, login_to_user.password_hashed_and_salted):
            if request.form.get('rememberMe') is True:
                login_user(login_to_user, remember=True)
                flash('Hi ' + login_to_user.username +
                      ' - Your Login was succesfull', 'success')
            else:
                login_user(login_to_user, remember=False)
                flash('Hi ' + login_to_user.username +
                      ' - Your Login was succesfull', 'success')
        else:
            flash('Password was not correct', 'danger')
            return render_template('loginUser.html', form=user_form, search_form=searchForm.SearchForm())

        nav.nav.register_element("frontend_top", view.nav_bar())
        if url:
            return redirect(url)
        else:
            return redirect(url_for('start'))
    return render_template('loginUser.html', form=user_form, search_form=searchForm.SearchForm())


# //TODO I have to define where to redirect when login_required is not okay
nav.login_manager.login_view = '/login/'


@app.route('/deleteUser/', methods=['GET', 'POST'])
@login_required
def delete_user():
    view.logged_user = view.get_logged_user()
    nav.nav.register_element("frontend_top", view.nav_bar())
    user_form = deleteUserForm.DeleteUser(request.form)
    if request.method == 'POST':
        if data_Structure.User.query.get(
                user_form.uid.data) is None:  # check if board already exists
            flash('User does not exist!', 'danger')
            return redirect(url_for('delete_user'))
        dele_user = data_Structure.User.query.get(user_form.uid.data)
        if pbkdf2_sha256.verify(user_form.password.data, dele_user.password_hashed_and_salted):
            data_Structure.db.session.object_session(
                dele_user).delete(dele_user)
            data_Structure.db.session.commit()
        else:
            flash('Password was incorrect!', 'danger')
            return redirect(url_for('delete_user'))
        # Skipping the next test because I never needed it until now!
        # if data_Structure.Board.query.filter_by(
        #       code=board_form.code.data).scalar() is not None:  # check if board already exists
        #    return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm(),
        #                          messages=messages.Messages(True, 'Board was not deleted!'))
        # check if User exists
        if data_Structure.User.query.get(user_form.uid.data) is None:
            flash('User was deleted successfully!', 'success')
            return render_template('deleteUserForm.html', form=user_form, search_form=searchForm.SearchForm())
    return render_template('deleteUserForm.html', form=user_form, search_form=searchForm.SearchForm())


@app.route('/registeredUsers/')
@login_required
def show_registered_users():
    view.logged_user = view.get_logged_user()
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template('userTable.html', args=data_Structure.User.query.all(), search_form=searchForm.SearchForm())


@app.route('/', methods=['GET', 'POST'])
def start():
    view.logged_user = view.get_logged_user()
    nav.nav.register_element("frontend_top", view.nav_bar())
    search_form = searchForm.SearchForm(request.form)
    results_board = None
    results_project = None
    results_component = None
    results_comments = None
    results_devices = None
    if request.method == 'POST':
        if request.form.get('submit_main') is None:
            search_word = request.form.get('search_field')
            search_area = request.form.get('Selector')
            

        else:
            search_word = request.form.get('search_field_main')

            search_area = 'All'
        if "EXB" in search_word and "Q" in search_word:
            search_word = clean_exb_scan(search_word)
            exb_number = data_Structure.Exb.query.get(search_word)
            if exb_number:
                component = exb_number.associated_components
                return redirect(url_for('show_component', component_id=component.id))
        elif "EXB" in search_word:
            search_word = search_word.strip()
            exb_number = data_Structure.Exb.query.get(search_word)
            if exb_number:
                component = exb_number.associated_components
                return redirect(url_for('show_component', component_id=component.id))
        if data_Structure.db.session.query(data_Structure.Board).get(search_word) is not None:
            return redirect(url_for('show_board_history',
                                    g_code=data_Structure.db.session.query(data_Structure.Board).get(search_word).code))
        if search_area == 'Boards' or search_area == 'All':
            if search_word is "":
                results_board = data_Structure.Board.query.all()
            else:
                results_board = search.search(search_word=search_word, items=data_Structure.Board.query.all())
        
        if search_area == 'Projects' or search_area == 'All':
            if search_word is "":
                results_project = data_Structure.Project.query.all()
            elif search_word is not "":
                results_project = search.search(search_word=search_word, items=data_Structure.Project.query.all())                    
            

        if search_area == 'Components' or search_area == 'All':
            if search_word is "":
                results_component = data_Structure.Component.query.all()
            else:
                components = data_Structure.Component.query.all()
                results_component = search.search(search_word, components)

        if search_area == 'All':
            results_comments = None
            if search_word is not "":
                results_comments = search.search(search_word=search_word, items=data_Structure.History.query.all())
                print("Platinen.py "+str(results_comments))
        if search_area == 'All' or search_area =='Devices':
            if search_word == "":
                results_devices = data_Structure.Device.query.all()
            elif search_word is not "":
                results_devices = search.search(search_word=search_word, items=data_Structure.Device.query.all()) 

        if not results_board and not results_project and not results_component and not results_comments and not results_devices:
            flash('No results were found', 'warning')
            return render_template('base.html')

        return render_template('table.html', args=results_board, projects=results_project,
                               search_form=searchForm.SearchForm(), search_word=search_word, components=results_component,
                               results_comments=results_comments, results_devices=results_devices)
    return render_template('start.html', search_form=search_form)



@app.route('/addBoard/scripted/test/', methods=['POST'])
def add_board_scripted():
    board_id = request.args.get('board_id')
    project_name = request.args.get('project')
    ver=request.args.get('version')
    stat = request.args.get('status')
    arg = request.args.get('result')
    comment = request.args.get('comment')
    print(board_id)
    if not board_id and not project and not ver and not stat and not arg : 
        print('no Succes')
        return "No Success"
    board = data_Structure.Board.query.get(board_id)
    if board:
        print('Board exists')
        return "Success"#redirect(url_for('show_board_history', g_code=board_id))
    else:
        new_board=data_Structure.Board(board_id,project_name,ver)
        new_board.args(['Test',arg])
        print(new_board)
        data_Structure.db.session.add(new_board)
        data_Structure.db.session.commit()
        if comment:
            new_comment = data_Structure.History(comment, board_id)
            data_Structure.db.session.add(new_comment)
            data_Structure.db.session.commit()

        
        return "Success"


@app.route('/Project/show/all/', methods=['GET'])
def show_project_all():
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template('table.html', projects=data_Structure.Project.query.all())
                               
    return render_template('start.html', search_form=search_form)



@app.route('/addBoard/', methods=['GET', 'POST'])
def add__board():
    view.logged_user = view.get_logged_user()
    nav.nav.register_element("frontend_top", view.nav_bar())
    board_form = addPlatineForm.BoardForm(request.form)
    board_form.name.choices = addPlatineForm.load_choices()
    add_project_form = project_forms.AddProjectForm(request.form)
    if request.method == 'POST':
        if data_Structure.Board.query.filter_by(
                code=board_form.code.data).scalar() is not None:  # check if board already exists
            flash('Board does already exist in the database!', 'danger')
            return render_template('addPlatineForm.html', add_project_form=add_project_form, form=board_form,
                                   search_form=searchForm.SearchForm())
        new_board = data_Structure.Board(code=board_form.code.data, project_name=board_form.name.data,
                                         ver=board_form.ver.data)
        data_Structure.db.session.add(new_board)
        data_Structure.db.session.commit()
        project = data_Structure.db.session.query(
            data_Structure.Project).get(new_board.project_name)
        project.project_boards.append(new_board)
        data_Structure.db.session.commit()
        if data_Structure.Board.query.filter_by(code=new_board.code).scalar() is not None:
            # if Board is now available
            flash('Board was successfully added!', 'success')
            label_file_cont = board_labels.generate_label(new_board.code)
            board_labels.write_doc(label_file_cont)
            board_labels.print_label("labelprinter01.sdi.site", "root", "0000")
            return render_template('addPlatineForm.html', add_project_form=add_project_form, form=board_form,
                                   search_form=searchForm.SearchForm())

        return redirect(url_for("spitOut"))

    return render_template('addPlatineForm.html', add_project_form=add_project_form, form=board_form,
                           search_form=searchForm.SearchForm())


@app.route('/Projects/Boards_belonging_to/<project_name>/', methods=['POST', 'GET'])
def show_boards_of_project(project_name):
    view.logged_user = view.get_logged_user()
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template('table.html', args=data_Structure.Board.query.filter_by(project_name=project_name).all())


@app.route('/add_Project/', methods=['POST', 'GET'])
@login_required
def add_project():
    view.logged_user = view.get_logged_user()
    nav.nav.register_element("frontend_top", view.nav_bar())
    add_project_form = project_forms.AddProjectForm(request.form)
    if request.method == 'POST':
        # check if Project already exists
        if data_Structure.Project.query.get(add_project_form.project_name.data) is not None:
            flash('Project ' + add_project_form.project_name.data +
                  ' already exists!', 'danger')
            return render_template('add_project.html', add_project_form=add_project_form)
        elif data_Structure.Project.query.get(add_project_form.project_name.data) is None:
            image_path = 'NE'
            filename = None
            if 'upfile' not in request.files:  # //TODO I still need to  check if files are safe
                image_path = None
            file = request.files.get('upfile')
            if file.filename is '':
                image_path = None
            elif file and image_path is 'NE':
                file_id = id(file.filename)
                filename = secure_filename(str(file_id) + file.filename)

                image_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(image_path)

            project_to_add = data_Structure.Project(project_name=add_project_form.project_name.data,
                                                    project_description=add_project_form.project_description.data,
                                                    project_default_image_path=filename)

            data_Structure.db.session.add(project_to_add)
            data_Structure.db.session.commit()
            flash('Project '+project_to_add.project_name+" was added.", "success")

            if str(request.form.get('add_platine')) in 'true':
                return redirect(url_for('add__board'))
            return redirect(url_for('start'))
    return render_template('add_project.html', add_project_form=add_project_form)


def delete_history_all(history):
    for obj in history.data_objects:
        image_to_delete = data_Structure.db.session.query(
            data_Structure.Files).get(int(obj.id))
        # board = data_Structure.db.session.query(data_Structure.board).get(int(board_id))

        os.remove(os.path.join(UPLOAD_FOLDER, image_to_delete.file_path))
        data_Structure.db.session.delete(image_to_delete)
        data_Structure.db.session.commit()
    data_Structure.db.session.delete(history)
    data_Structure.db.session.commit()


@app.route('/deleteBoard/', methods=['GET', 'POST'])
@login_required
def del_board(board_delete=None):
    view.logged_user = view.get_logged_user()
    nav.nav.register_element("frontend_top", view.nav_bar())
    board_form = delPlatineForm.delBoardForm(request.form)
    if request.method == 'POST':
        if data_Structure.Board.query.filter_by(
                code=board_form.code.data).scalar() is None:  # check if board already exists
            flash('Board does not exist!', 'danger')
            return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm())
        if board_delete is None:
            dele_board = data_Structure.Board.query.filter_by(
                code=board_form.code.data).first()
        elif board_delete is not None:
            dele_board = board_delete
        for history in data_Structure.History.query.filter_by(board_code=dele_board.code).all():
            delete_history_all(history)

        data_Structure.db.session.delete(dele_board)
        data_Structure.db.session.commit()
        if data_Structure.Board.query.filter_by(
            code=board_form.code.data).scalar() is not None or data_Structure.db.session.query(
                data_Structure.Board).get(dele_board.code):  # check if board still exists
            flash('Somehow the board could not be deleted', 'danger')
            return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm())
        if data_Structure.Board.query.filter_by(
                code=board_form.code.data).scalar() is None and board_delete is None:  # check if board already exists
            flash('Board was successfully deleted!', 'success')
            return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm())
    return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm())


def edit_board_history(board, history_id, history):
    nav.nav.register_element("frontend_top", view.nav_bar())

    history_to_edit = data_Structure.History.query.get(history_id)
    history_to_edit.history = history.replace('\n', "<br>")
    history_to_edit.last_edited = time.strftime("%d.%m.%Y %H:%M:%S")
    history_to_edit.edited_by = data_Structure.db.session.query(data_Structure.User).get(
        data_Structure.User.get_id(current_user))
    data_Structure.db.session.commit()

    return redirect(url_for('show_board_history', g_code=board.code))


def add_board_history(board, history, file):
    new_history = data_Structure.History(
        history=history, board_code=board.code)
    if file:
        file_id = id(file.filename)
        filename = secure_filename(str(file_id) + file.filename)

        image_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(image_path)
        file_to_add = data_Structure.Files(
            history=new_history, file_path=filename)
        data_Structure.db.session.add(file_to_add)

    data_Structure.db.session.add(new_history)

    data_Structure.db.session.commit()
    return redirect(url_for('show_board_history', g_code=board.code))



def getSortKeyHistory(h):
    return h.time_date_datetime()


@app.route('/boardHistory/<g_code>/', methods=['POST', 'GET', ])  # shows board History
def show_board_history(g_code):
    view.logged_user = view.get_logged_user()
    nav.nav.register_element("frontend_top", view.nav_bar())
    tg_board = data_Structure.Board.query.get(g_code)
    add_form = HistoryForm(request.form)
    edit_form = EditHistoryForm(request.form)

    if request.method == 'POST' and add_form.send.data:

        file = request.files.get('file')

        add_board_history(
            board=tg_board, history=add_form.history.data, file=file)
    elif request.method == 'POST' and edit_form.send_edit.data:
        edit_board_history(board=tg_board, history=edit_form.history.data,
                           history_id=edit_form.history_id.data)
    elif request.method == 'POST' and edit_form.delete.data:
        history = data_Structure.History.query.get(
            int(edit_form.history_id.data))
        delete_history_all(history)

    if edit_form is not None:
        return render_template('boardHistory.html', g_board=tg_board,
                               history=sorted(data_Structure.History.query.filter_by(board_code=g_code).all(),
                                              key=getSortKeyHistory, reverse=True),
                               # .order_by(lambda e:
                               # data_Structure.History.time_date_datetime(e).desc()).all(),
                               add_form=add_form, edit_form=edit_form)
    else:
        return render_template('boardHistory.html', g_board=tg_board,
                               history=sorted(data_Structure.History.query.filter_by(board_code=g_code).all(),
                                   key=getSortKeyHistory, reverse=True),
                               add_form=add_form, edit_form=edit_form)


@app.route('/ProjectPage/<project_name>/', methods=['POST', 'GET'])
def show_project(project_name):
    view.logged_user = view.get_logged_user()
    nav.nav.register_element("frontend_top", view.nav_bar())
    project = data_Structure.Project.query.get(project_name)
    if project is None:
        flash('Project "' + project_name + '" was not found!', 'danger')
        return render_template('start.html')
    # boards_of_project = data_Structure.Board.query.filter_by(project_name=project_name)
    # boards_of_project)
    return render_template('ProjectPage.html', project=project, boards=project.project_boards)


@app.route('/project/change/description/<project_name>/', methods=['POST'])
@login_required
def change_project_description(project_name):
    project = data_Structure.Project.query.get(project_name)
    new_description = request.form.get('project_description_form')
    project.project_description = new_description
    data_Structure.db.session.commit()
    return redirect(url_for('show_project', project_name=project_name))


@app.route('/project/delete/image/<project_name>/', methods=['POST'])
@login_required
def delete_project_image(project_name):
    view.logged_user = view.get_logged_user()
    # image_to_delete = data_Structure.db.session.query(data_Structure.Files).get(int(img_id))
    project = data_Structure.db.session.query(
        data_Structure.Project).get(project_name)
    img_id = project.project_default_image_path
    # img_id = None
    project.project_default_image_path = None
    if img_id is not None:
        os.remove(os.path.join(UPLOAD_FOLDER, img_id.replace('_', '\\')))

    # data_Structure.db.session.delete(image_to_delete)
    data_Structure.db.session.commit()

    return redirect(url_for('show_project', project_name=project_name))


@app.route('/project/edit/image/<project_name>', methods=['POST'])
@login_required
def edit_project_image(project_name):
    view.logged_user = view.get_logged_user()
    project = data_Structure.db.session.query(
        data_Structure.Project).get(project_name)
    file = request.files.get('new_upfile')
    if file:
        file_id = id(file.filename)
        filename = secure_filename(str(file_id) + file.filename)
        if ".jpg" in filename.lower() or ".jpeg" in filename.lower() or ".bmp" in filename.lower():
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            if project.project_default_image_path is not None:
                os.remove(os.path.join(UPLOAD_FOLDER,
                                       project.project_default_image_path))
            project.project_default_image_path = filename
            # print(filename)
            data_Structure.db.session.commit()
            flash('Picture was changed successfully!', 'success')
        else:
            flash(
                'Your uploaded File was propably not a Picture. Pleas use only JPEG(jpeg) or JPG(jpg) or BMP(bmp) Pictures!',
                'danger')
    return redirect(url_for('show_project', project_name=project_name))


@app.route('/boardHistory/delete/image/<img_id>/<board_id>/', methods=['POST'])
@login_required
def delete_history_image(img_id, board_id):
    view.logged_user = view.get_logged_user()
    image_to_delete = data_Structure.db.session.query(
        data_Structure.Files).get(int(img_id))
    # board = data_Structure.db.session.query(data_Structure.board).get(int(board_id))

    os.remove(os.path.join(UPLOAD_FOLDER, image_to_delete.file_path))
    # os.remove(str(DATA_FOLDER + image_to_delete.file_path.replace('/', '\\')))
    data_Structure.db.session.delete(image_to_delete)
    data_Structure.db.session.commit()

    return redirect(url_for('show_board_history', g_code=board_id))


@app.route('/boardHistory/add/file/<history_id>/<board_id>', methods=['POST'])
@login_required
def board_history_add_file(history_id, board_id):
    view.logged_user = view.get_logged_user()
    history = data_Structure.db.session.query(
        data_Structure.History).get(int(history_id))
    file = request.files.get(str(history_id) + 'new_upfile')
    if file:
        file_id = id(file.filename)
        filename = secure_filename(str(file_id) + file.filename)

        image_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(image_path)
        file_to_add = data_Structure.Files(history=history, file_path=filename)
        data_Structure.db.session.add(file_to_add)
        data_Structure.db.session.commit()
    return redirect(url_for('show_board_history', g_code=board_id))


@app.route('/project/delete/project/<project_name>/', methods=['POST'])
@login_required
def delete_project(project_name):
    view.logged_user = view.get_logged_user()
    project_to_delete = data_Structure.db.session.query(
        data_Structure.Project).get(project_name)

    for board in project_to_delete.project_boards:
        for history in board.history:
            for file in history.data_objects:
                os.remove(os.path.join(UPLOAD_FOLDER, file.file_path))
                data_Structure.db.session.delete(file)

            data_Structure.db.session.delete(history)
        data_Structure.db.session.delete(board)
    data_Structure.db.session.commit()
    if project_to_delete.project_default_image_path is not None:
        os.remove(os.path.join(UPLOAD_FOLDER,
                               project_to_delete.project_default_image_path))
    data_Structure.db.session.delete(project_to_delete)
    data_Structure.db.session.commit()
    return redirect(url_for('start'))


@app.route('/my_profile/')
def my_profile():
    view.logged_user = view.get_logged_user()
    if current_user.username is 'Guest':
        return redirect(url_for('start'))
    nav.nav.register_element("frontend_top", view.nav_bar())

    return render_template('userProfile.html')


@app.route('/my_profile/change/username/<uid>/', methods=['POST'])
@login_required
def change_username(uid):
    user_to_change = data_Structure.db.session.query(
        data_Structure.User).filter_by(uid=uid).first()

    new_username = request.form.get('new_username')

    if not data_Structure.db.session.query(data_Structure.User).filter_by(username=str(new_username)).all():
        user_to_change.username = new_username
        data_Structure.db.session.commit()
        flash("Username was changed sucesfully to \"" +
              new_username + "\"", "success")
    else:
        flash("Username \"" + new_username +
              "\" already exists. Please choose another Username", "danger")
        print("Hallo")
    return redirect(url_for('my_profile'))


@app.route('/my_profile/change/email/<uid>/', methods=['POST'])
@login_required
def change_email(uid):
    user_to_change = data_Structure.db.session.query(
        data_Structure.User).filter_by(uid=uid).first()

    new_email = request.form.get('new_email')
    user_to_change.email = new_email
    data_Structure.db.session.commit()
    return redirect(url_for('my_profile'))


@app.route('/my_profile/change/password/<uid>/', methods=['POST'])
@login_required
def change_password(uid):
    user_to_change = data_Structure.db.session.query(
        data_Structure.User).filter_by(uid=uid).first()

    if pbkdf2_sha256.verify(request.form.get('old_password'), user_to_change.password_hashed_and_salted):
        new_password_hash = pbkdf2_sha256.hash(
            request.form.get('new_password_1'))
        if pbkdf2_sha256.verify(request.form.get('new_password_2'), new_password_hash):
            user_to_change.password_hashed_and_salted = new_password_hash
            data_Structure.db.session.commit()
            flash('password was changed successful', 'success')
        else:
            flash('The new passwords did not match!', 'danger')
    else:
        flash('Your Password was incorrect', 'danger')
    return redirect(url_for('my_profile'))


@app.route('/my_profile/delete/me_myself_and_i/and_really_me_so_i_wont_be_able_to_visit_this_site_anymore/',
           methods=['POST'])
def delete_myself():
    user_to_delete = data_Structure.db.session.query(
        data_Structure.User).get(current_user.uid)
    password_1 = request.form.get('password_1')
    password_2 = request.form.get('password_2')
    if pbkdf2_sha256.verify(password_1, user_to_delete.password_hashed_and_salted) \
            and pbkdf2_sha256.verify(password_2, user_to_delete.password_hashed_and_salted):
        logout_user()
        data_Structure.db.session.delete(user_to_delete)
        data_Structure.db.session.commit()
        flash('User ' + str(user_to_delete.username) + ' was succesfully deleted')
        return redirect(url_for('start'))
    else:
        flash('Wrong Password(s)', 'danger')
        return redirect(url_for('my_profile'))


@app.route('/user_forgot_password/', methods=['GET'])
@login_required
def user_forgot_password():
    nav.nav.register_element("frontend_top", view.nav_bar())
    flash('Pleas enter the uid, you can find it if you look for the user at ' + '<a href="' + url_for(
        'show_registered_users') + '">Registered Users</a>', 'info')
    return render_template('forgot_password.html')


# Sorry for the dumb user, I could not find a better word for this variable... :D
@app.route('/user_forgot_password/change_password/', methods=['POST'])
@login_required
def user_forgot_change_password():
    logged_user = data_Structure.db.session.query(
        data_Structure.User).get(current_user.uid)
    dumb_user_id = request.form.get('uid')
    dumb_user = None
    if dumb_user_id:
        dumb_user = data_Structure.db.session.query(
            data_Structure.User).get(int(dumb_user_id))
    if not dumb_user:
        flash('User does not exist! (UID: ' + str(dumb_user_id) + ')', 'danger')
        return redirect(url_for(user_forgot_password))
    if pbkdf2_sha256.verify(request.form.get('current_user_password'), logged_user.password_hashed_and_salted):
        new_password = pbkdf2_sha256.hash(request.form.get('new_password_1'))
        if pbkdf2_sha256.verify(request.form.get('new_password_2'), new_password):
            dumb_user.password_hashed_and_salted = new_password
            data_Structure.db.session.commit()
            flash('password of ' + dumb_user.username + ' was changed successfully', 'success')
            return redirect(url_for('start'))
        else:
            flash('The new passwords did not match!', 'danger')
            return redirect(url_for(user_forgot_password))
    else:
        flash(current_user.username + ' your password was not correct!', 'danger')
        return redirect(url_for(user_forgot_password))


@app.route('/boardHistory/change/version/<board_id>/', methods=['POST'])
@login_required
def change_board_version(board_id):
    board = data_Structure.Board.query.get(board_id)
    new_version = request.form.get('version_form')
    comment_string = "Version was changed from " + \
        board.version + " to " + new_version
    change_comment = data_Structure.History(comment_string, board.code)
    data_Structure.db.session.add(change_comment)
    board.version = new_version
    data_Structure.db.session.commit()
    return redirect(url_for('show_board_history', g_code=board_id))


@app.route('/boardHistory/change/state/<board_id>/', methods=['POST'])
@login_required
def change_board_state(board_id):
    board = data_Structure.Board.query.get(board_id)
    new_state = request.form.get('state_form')
    comment_string = "State was changed from " + \
        str(board.stat) + " to " + new_state
    change_comment = data_Structure.History(comment_string, board.code)
    data_Structure.db.session.add(change_comment)
    board.stat = new_state
    data_Structure.db.session.commit()
    return redirect(url_for('show_board_history', g_code=board_id))


@app.route('/boardHistory/change/patch/<board_id>/', methods=['POST'])
@login_required
def change_board_patch(board_id):
    board = data_Structure.Board.query.get(board_id)
    new_patch = request.form.get('patch_form')
    comment_string = "Patch was changed from " + \
        str(board.patch) + " to " + new_patch
    change_comment = data_Structure.History(comment_string, board.code)
    data_Structure.db.session.add(change_comment)
    board.patch = new_patch
    data_Structure.db.session.commit()
    return redirect(url_for('show_board_history', g_code=board_id))

@app.route('/upgrade/')
@login_required
def upgrade_within_app():
    migrate_database()
    return redirect(url_for("start"))

@app.route('/board/edit_args/', methods=['POST'])
def edit_args():
    arg_name = request.form.get('name')
    board_id = request.args.get('board_id')
    board = data_Structure.Board.query.get(board_id)
    if request.form.get('delete_btn') is not None:
        res = board.args(arg_name, delete=True)
        data_Structure.db.session.commit()
        if res:
            flash(res+" was deleted", 'success')
        return redirect(url_for('show_board_history', g_code=board_id))

    arg_value = request.form.get('value')

    
    board.args([arg_name,arg_value])
    data_Structure.db.session.commit()

    return redirect(url_for('show_board_history', g_code=board_id))

@app.route('/device/add/do/', methods=['POST'])
def add_device_do():
    device_name = request.form.get('device_name')
    device_brand = request.form.get('device_brand')
    
    if device_brand and device_name:
        device = data_Structure.Device(device_name, device_brand)
        try:
            data_Structure.db.session.add(device)
            data_Structure.db.session.commit()
        except:
            flash('An error occured while adding the device to the database', 'danger')
            return redirect(url_for('start'))
    flash('device \"'+device_name+'\" was added.', "success")
    return redirect(url_for('add_device'))

@app.route('/device/add/', methods=['GET'])
def add_device():
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template('add_device.html')

@app.route('/device/args/change/', methods=['POST'])
def device_args():
    arg_name = request.form.get('name')
    try:
        device_id = int(request.args.get('device_id'))
    except:
        flash('could not convert string to int: device_args()', 'danger')
        return redirect(url_for('start'))
    device = data_Structure.Device.query.get(device_id)
    if request.form.get('delete_btn') is not None:
        res = device.args(arg_name, delete=True)
        data_Structure.db.session.commit()
        if res:
            flash(res+" was deleted", 'success')
        return redirect(url_for('show_device', device_id=device_id))
    elif request.form.get('change_btn') is not None:
        arg_value = request.form.get('value')
        device.args([arg_name, arg_value])
        data_Structure.db.session.commit()
        return redirect(url_for('show_device', device_id=device_id))
    flash('some error occured //device_args()//', 'warning')
    return redirect(url_for('show_device', device_id=device_id))


@app.route('/device/show/<device_id>/', methods=['GET'])
def show_device(device_id):
    nav.nav.register_element("frontend_top", view.nav_bar())
    device=data_Structure.Device.query.get(int(device_id))
    return render_template('device_page.html', device=device)

@app.route('/device/upload/document/', methods=['POST'])
def upload_device_document():
    print('UPLOAD')
    try:
        device = data_Structure.Device.query.get(int(request.args.get('device_id')))
    except:
        flash('An error occured //upload_device_document()//', 'danger')
        return redirect(url_for('start'))
    file = request.files['device_documents']
    print(request.method)
    if file:
        file_id = id(file.filename)
        filename = secure_filename('devdoc_'+str(file_id) + file.filename)
        

        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        file_to_add = data_Structure.DeviceDocument(os.path.join(RELATIVE_PICTURE_PATH, filename), device)
        data_Structure.db.session.add(file_to_add)
        data_Structure.db.session.commit()
        flash('file was uploaded successful.', 'success')
    else:
        print('no file attached')
    return redirect(url_for('show_device', device_id=device.device_id))

@app.route('/device/delete/do/', methods=['POST'])
def delete_device():
    try:
        device = data_Structure.Device.query.get(int(request.args.get('device_id')))
    except:
        flash('An error Occured //delete_device()//', 'danger')
        return redirect(url_for('start'))
    
    for doc in device.device_documents:
        delete_document_func(doc)

    data_Structure.db.session.delete(device)
    data_Structure.db.session.commit()
    return redirect(url_for('start'))

@app.route('/device/delete/document/do/', methods=['POST'])
def delete_document():
    try:
        device_id = int(request.args.get('device_id'))
        document = data_Structure.DeviceDocument.query.get(int(request.args.get('document_id')))

    except:
        flash('An error Occured //delete_document()//', 'danger')
        return redirect(url_for('start'))
    if delete_document_func(document):
        flash('document was deleted successful', 'success')
    else:
        flash('An error occured //delete_document_func()', 'danger')
    
    return redirect(url_for('show_device', device_id=device_id))

@app.route('/label/print/do/', methods=['POST'])
def print_label():
    text = request.form.get('text')
    label = board_labels.generate_label(text)
    board_labels.write_doc(label)
    board_labels.print_label("labelprinter01.sdi.site")
    return redirect(url_for('show_new_label'))

@app.route('/label/print/new/', methods=['GET'])
def show_new_label():
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template('new_label.html')
def delete_document_func(document):
    try:
        os.remove(os.path.join(DATA_FOLDER, document.device_document_path))
    except:
        return False
    data_Structure.db.session.delete(document)
    data_Structure.db.session.commit()
    return True

def test_queries():
    with app.app_context():
        migrate_database()

@app.route('/component/add/', methods=['GET'])
def add_component():
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template('add_component.html')


@app.route('/component/add/do/create/', methods=['POST'])
def create_component():
    # flash("create_component was called!", "danger")
    # print(request.form)
    # print(request.files)
    new_component = data_Structure.Component()
    if request.form.get('description'):
        description = request.form.get('description')

    else:
        description = None
        flash('The field description is required!', "danger")
        return redirect(url_for('add_component'))
    new_component.description = description
    if request.form.get('select_smd_thd') == 'SMD':
        smd = True
    else:
        smd = False
    new_component.smd = smd
    if request.form.get('select_housing') is not '':
        housing_id = int(request.form.get('select_housing'))
    else:
        # housing_id = None
        flash(
            "you did something interesting. please remember your action and mail to" +
            " <a href=\"mailto:stefan.steinmueller@siemens.com?Subject=create_component_error\">Stefan Steinmueller</a>",
            "danger")
        return redirect(url_for('add_component'))
    new_component.housing_id = housing_id
    if request.form.get('select_category') is not '0':
        category_id = int(request.form.get('select_category'))
    elif request.form.get('select_category') is '0':
        category_id = 0
        flash("Please select a category!", "warning")
        return redirect(url_for('add_component'))

    new_component.category_id = category_id
    if request.form.get('man_id') is not '':
        man_id = request.form.get('man_id')
    else:
        flash("Please enter the manufacturer ID", "warning")
        return redirect(url_for('add_component'))
    new_component.manufacturer_id = man_id
    if request.form.get('manufacturer') is not '':
        print('manufacturer is not none')
        manufacturer = request.form.get('manufacturer')
        new_component.manufacturer = manufacturer
        print(new_component.manufacturer)
    else:
        flash("Please enter the name of a manufacturer!")
        return redirect(url_for('add_component'))
    # new_component.manufacturer = manufacturer
    if request.form.get('packaging_type') is not '':
        packaging_id = int(request.form.get('packaging_type'))
    else:
        packaging_id = None
        flash("you did something interesting. please remember your action and mail to" +
              " <a href=\"mailto:stefan.steinmueller@siemens.com?Subject=create_component_error_packaging_type\">Stefan Steinmueller</a>",
              "danger")
    new_component.packaging_id = packaging_id
    value = ''

    if request.form.get('value') is not '':
        value += str(request.form.get('value'))

    if request.form.get('scale') is not '':
        value += str(data_Structure.scale[int(request.form.get('scale'))])
    if request.form.get('unit') is not '':
        value += str(data_Structure.unit[int(request.form.get('unit'))])
        # print("value  : " + value)
    new_component.value = value
    if request.form.get('chip_form') is not '':
        chip_form = request.form.get('chip_form')
        if chip_form not in data_Structure.chip_forms:

            new_component.chip_form = ''
        else:
            new_component.chip_form = chip_form

    # datasheet = None
    if 'datasheet' not in request.files:
        flash('No datasheet was selected!', "warning")

    elif 'datasheet' in request.files:
        file = request.files['datasheet']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No datasheet was selected!', "warning")

        if file:
            filename = str(id(os.urandom(6))) + secure_filename(file.filename)
            filepath = os.path.join(DATA_UPLOAD_FOLDER, filename)
            file.save(filepath)
            datasheet = data_Structure.Documents(document_type="Datasheet",file_name=filename)
            data_Structure.db.session.add(datasheet)
            new_component.datasheet = datasheet

    # EXB Number

    exb = request.form.get('exb_number')
    if '@' in exb:
        exb = clean_exb_scan(exb)

    # print("exb :" + exb)
    if exb is '' or exb is None:
        if request.form.get('division_select') is None:
            flash("Please enter either a EXB number or your division!", "warning")
            return redirect(url_for('add_component'))
            # print('new_exb should be called!')
        exb_number = data_Structure.Exb(
            division=request.form.get('division_select'))
    elif data_Structure.db.session.query(data_Structure.Exb).get(exb) is None:
        exb_number = data_Structure.Exb(exb_number=exb)

    else:
        flash("The Exb Number does already exist. Please take another one!", "warning")
        return redirect(url_for('add_component'))
    data_Structure.db.session.add(exb_number)
    new_component.exb_number = exb_number

    data_Structure.db.session.add(new_component)
    data_Structure.db.session.commit()
    return redirect(url_for('add_component'))


@app.route('/component/show/', methods=['GET'])
def show_all_components():
    nav.nav.register_element("frontend_top", view.nav_bar())
    exb_numbers = data_Structure.Exb.query.all()
    print (exb_numbers)
    return render_template('component_table.html', exb_numbers=exb_numbers)


@app.route('/component/show/<component_id>/', methods=['GET'])
def show_component(component_id):
    nav.nav.register_element("frontend_top", view.nav_bar())
    component = data_Structure.Component.query.get(component_id)
    if component.taken_out:
        booking = data_Structure.Booking.query.filter_by(component_id = component.id).all()[::-1][0]
        process = data_Structure.Process.query.get(booking.process_id)
        flash("Component is out for placement. ("+process.user().username+")","danger")
    return render_template('component.html', component=component)


@app.route('/component/stocktaking/stock/', methods=['GET'])
@app.route('/component/stocktaking/stock/<component_id>/', methods=['GET'])
@login_required
def stocktaking_stock(component_id=None):
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template('stocktaking.html')


@app.route('/component/stocktaking/stock/post/', methods=['POST'])
@login_required
def stocktaking_stock_do():
    exb_number = request.form.get('exb_number')
    if '@' in exb_number:
        exb_number = clean_exb_scan(exb_number)
    component = data_Structure.db.session.query(
        data_Structure.Exb).get(exb_number)

    if component is None:
        flash("Some error occured, maybe your EXB number is invalid?")
        return redirect(url_for('stocktaking_stock'))
    else:
        component = component.associated_components
    if component.taken_out:  # if this component is taken out, it is not very good to count it while its away
        flash("Component was taken out by " + data_Structure.db.session.query(data_Structure.Booking).filter_by(
            component_id=component.id).order_by(data_Structure.Booking.date_time).first().user().username, "danger")
        return redirect(url_for('stocktaking_stock'))
    for b in data_Structure.Booking.query.filter_by(deprecated=False, lab=False).join(data_Structure.Component,
                                                                                      data_Structure.Booking.component_id == component.id).all():
        b.deprecated = True
    booking = data_Structure.Booking(
        int(request.form.get('qty')), "Stocktaking")
    booking.component = component
    data_Structure.db.session.add(booking)
    data_Structure.db.session.commit()
    return redirect(url_for('stocktaking_stock'))


@app.route('/component/edit/datasheet/<component_id>/', methods=['POST'])
def upload_datasheet(component_id):
    component = data_Structure.Component.query.get(int(component_id))
    print(request.files)
    if 'datasheet' in request.files:
        file = request.files['datasheet']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No datasheet was selected!', "warning")

        if file:
            filename = str(id(os.urandom(6))) + secure_filename(file.filename)
            filepath = os.path.join(DATA_UPLOAD_FOLDER, filename)
            file.save(filepath)
            datasheet = data_Structure.Documents(
                document_type="Datasheet", file_name=filename)
            data_Structure.db.session.add(datasheet)
            component.documents.append(datasheet)
            data_Structure.db.session.commit()
    elif not 'datasheet' in request.files:
        flash('No datasheet was selected!', "warning")

    return redirect(url_for('show_component', component_id=component_id))


@app.route('/component/stocktakiing/lab/do/<component_id>/', methods=['POST'])
def stocktaking_lab(component_id):
    component = data_Structure.Component.query.get(int(component_id))
    for b in data_Structure.Booking.query.filter_by(component_id=component_id, lab=True).all():
        b.deprecated = True

    new_booking = data_Structure.Booking(
        booking_type="purchase", qty=int(request.form.get('stock_lab')), component=component)
    new_booking.lab = True

    data_Structure.db.session.add(new_booking)
    data_Structure.db.session.commit()
    return redirect(url_for('show_component', component_id=component_id))


@app.route('/component/take/lab/do/<component_id>/', methods=['POST'])
def take_lab(component_id):
    component = data_Structure.Component.query.get(int(component_id))
    new_booking = data_Structure.Booking(booking_type="removal", qty=int(
        request.form.get('qty_lab_out')), component=component)
    new_booking.lab = True

    data_Structure.db.session.add(new_booking)
    data_Structure.db.session.commit()
    return redirect(url_for('show_component', component_id=component_id))


@app.route('/component/datasheet/delete/<component_id>/do/', methods=['POST'])
def delete_datasheet(component_id):
    component = data_Structure.Component.query.get(int(component_id))
    file = component.datasheet()
    filepath = os.path.join(DATA_UPLOAD_FOLDER, file.file_name)
    component.datasheet = None
    data_Structure.db.session.delete(file)

    try:
        os.remove(filepath)
    except:
        flash("File could not be deleted", "danger")
        return redirect(url_for('show_component', component_id=component_id))
    flash("file was deleted succesful", "success")
    data_Structure.db.session.commit()
    return redirect(url_for('show_component', component_id=component_id))


@app.route('/component/bringback/', methods=['GET', 'POST'])
@app.route("/component/bringback/<component_id>/", methods=['GET', 'POST'])
@login_required
def bring_back(component_id=None):
    nav.nav.register_element("frontend_top", view.nav_bar())

    if component_id:
        component = data_Structure.Component.query.get(int(component_id))
    else:
        component = None

    if request.method == 'POST':

        if not component:
            exb = data_Structure.Exb.query.get(request.form.get('exb'))
            if exb:
                component = exb.associated_components
        if not component:
            flash("Component cannot be found!", "danger")
            return redirect(url_for('bring_back'))
        component.taken_out = False

        if request.form.get('qty'):
            #print("Stocktaking started...")
            for b in data_Structure.Booking.query.filter_by(deprecated=False, lab=False).join(data_Structure.Component,
                                                                                              data_Structure.Booking.component_id == component.id).all():
                b.deprecated = True
            booking = data_Structure.Booking(
                int(request.form.get('qty')), "Stocktaking")
            booking.component = component
            data_Structure.db.session.add(booking)
        data_Structure.db.session.commit()
        return redirect(url_for('bring_back'))
    return render_template('bringback.html', component=component)


@app.route('/component/reserve/<component_id>/', methods=['POST'])
@login_required
def reserve_component(component_id):
    qty = int(request.form.get('qty'))
    r = data_Structure.Reservation(qty)
    r.component = data_Structure.Component.query.get(int(component_id))
    p = data_Structure.Process()
    p.reservations.append(r)
    data_Structure.db.session.add(r)
    data_Structure.db.session.add(p)
    data_Structure.db.session.commit()
    return redirect(url_for('show_component', component_id=component_id))


@app.route('/process/book/<process_id>/', methods=['POST'])
@login_required
def book_process(process_id):
    process = data_Structure.Process.query.get(process_id)
    process.book()
    return redirect('my_profile')


@app.route('/process/order/component/', methods=['POST'])
def order_component():
    component_id = request.args.get('component_id')
    qty = request.form.get('qty')
    if component_id and qty:
        component = data_Structure.Component.query.get(int(component_id))
        order = data_Structure.Order(component=component, qty=qty)
        process = data_Structure.Process()
        data_Structure.db.session.commit()
        process.orders.append(order)
        data_Structure.db.session.add(process)
        data_Structure.db.session.commit()
        flash('order was placed!', 'success')
    return redirect(url_for('show_component', component_id=component_id))


@app.route('/process/order/confirm/', methods=['GET'])
def confirm_order():
    nav.nav.register_element("frontend_top", view.nav_bar())

    process = data_Structure.Process.query.filter_by(reservations=None, bookings=None).all()

    return render_template('confirm_order.html', process=process)

@app.route('/process/order/confirm/do/', methods=['POST'])
@login_required
def order_confirm_do():
    p = data_Structure.Process()
    form_data = request.form
    print(form_data)
    for key, qty in form_data.items():
        order = data_Structure.Order.query.get(int(key))
        if order.quantity == int(qty):
            p.bookings.append(order.book())

        else:
            p.bookings.append(order.book(quantity=int(qty)))
            flash('Order was not delivered completely!', 'warning')
    flash('order was confirmed succesfull', 'success')
    return redirect(url_for('confirm_order'))

@app.route('/process/reservations/delete/do/', methods=['POST'])
@login_required
def delete_process():
    process_id = int(request.args.get('process_id'))
    process = data_Structure.Process.query.get(process_id)

    for r in process.reservations:
        data_Structure.db.session.delete(r)
    data_Structure.db.session.delete(process)
    data_Structure.db.session.commit()
    flash('Process was deleted succesfully', "success")
    return redirect(url_for('my_profile'))

@app.route('/process/reservation/bom/', methods=['GET'])
@login_required
def bom_upload():
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template('bom_upload.html')

@app.route('/process/reservation/bom/do/', methods=['POST'])
@login_required
def bom_upload_do():
    bom_file = request.files['bom_file']
    description = request.form.get('description')
    #print(bom_file.read())
    temp = tempfile.mkstemp(dir=DATA_UPLOAD_FOLDER)
    with open(temp[1], 'wb') as open_temp:
        open_temp.write(bom_file.read())
    with open(temp[1], 'rt') as temp_bom:
        reservations = BOM_Converter.read_csv(temp_bom)
        print("REservations ReservationsReservations: "+str(reservations))
        process = data_Structure.Process(description=description)
        data_Structure.db.session.add(process)
        data_Structure.db.session.commit()
        for e in reservations:
            r = data_Structure.Reservation(int(e[1]))
            exb = data_Structure.Exb.query.get(e[0])
            if not exb:
                flash(e[0]+" was not found!", 'warning')
            else:
                r.component = data_Structure.Exb.query.get(e[0]).associated_components
                data_Structure.db.session.add(r)
                data_Structure.db.session.commit()
                print(r)
                process.reservations.append(r)
                print(process.reservations.all())
                data_Structure.db.session.commit()
                print("After Commit: "+str(process.reservations.all()))
        
        flash("reservation was made")

    
        
    return redirect(url_for('bom_upload'))

@app.route('/board/change/owner/do/<board_id>', methods=["POST"])
@login_required
def change_board_owner(board_id):
    board = data_Structure.Board.query.get(board_id)
    new_owner = request.form.get('owner_form')
    board.change_owner(new_owner)
    return redirect(url_for('show_board_history', g_code=board_id))

if __name__ == '__main__':
    # app.secret_key = 'Test'

    Bootstrap(app)
    SQLAlchemy(app)
    # nav.nav_logged_in.init_app(app)
    nav.nav.init_app(app)

    register_renderer(app, 'own_nav_renderer', ownNavRenderer.own_nav_renderer)
    app.secret_key = os.urandom(12)
    nav.login_manager.init_app(app)

    # login_manager is initialized in nav because I have to learn how to organize and I did not know that im able to
    # implement more files per python file and in nav was enough space.
    test_queries()
    app.run(debug=False, port=80, host='0.0.0.0')
    

    
# app.run(debug=False, port=80, host='0.0.0.0')
