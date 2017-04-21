import os
import time

from flask import render_template, request, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_login import login_user, logout_user, login_required, current_user
from flask_nav import register_renderer
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256
from werkzeug.utils import secure_filename


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
from data_Structure import app, db
from historyForm import HistoryForm, EditHistoryForm


nav.login_manager.anonymous_user = data_Structure.User

RELATIVE_PICTURE_PATH = 'static/Pictures'
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), RELATIVE_PICTURE_PATH)
DATA_FOLDER = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


# def set_logged_user(state):
#    logged_user = state


# data_Structure.db.create_all()
def is_logged_in():
    if session.get('logged_in'):
        return True
    else:
        return False


def delete_project():
    pass


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
                flash('There is already somone registered with the same Email adress!', 'danger')
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
        login_to_user = data_Structure.User.query.filter_by(username=user_form.username.data).first()
        if pbkdf2_sha256.verify(user_form.password.data, login_to_user.password_hashed_and_salted):
            if request.form.get('rememberMe') is True:
                login_user(login_to_user, remember=True)
                flash('Hi ' + login_to_user.username + ' - Your Login was succesfull', 'success')
            else:
                login_user(login_to_user, remember=False)
                flash('Hi ' + login_to_user.username + ' - Your Login was succesfull', 'success')
        else:
            flash('Password was not correct', 'danger')
            return render_template('loginUser.html', form=user_form, search_form=searchForm.SearchForm())

        nav.nav.register_element("frontend_top", view.nav_bar())
        if url:
            return redirect(url)
        else:
            return redirect(url_for('start'))
    return render_template('loginUser.html', form=user_form, search_form=searchForm.SearchForm())


nav.login_manager.login_view = '/login/'  # //TODO I have to define where to redirect when login_required is not okay


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
            data_Structure.db.session.object_session(dele_user).delete(dele_user)
            data_Structure.db.session.commit()
        else:
            flash('Password was incorrect!', 'danger')
            return redirect(url_for('delete_user'))
        # Skipping the next test because I never needed it until now!
        # if data_Structure.Board.query.filter_by(
        #       code=board_form.code.data).scalar() is not None:  # check if board already exists
        #    return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm(),
        #                          messages=messages.Messages(True, 'Board was not deleted!'))
        if data_Structure.User.query.get(user_form.uid.data) is None:  # check if User exists
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
    if request.method == 'POST':
        if request.form.get('submit_main') is None:
            search_word = request.form.get('search_field')
            search_area = request.form.get('Selector')

        else:
            search_word = request.form.get('search_field_main')

            search_area = 'All'
        if data_Structure.db.session.query(data_Structure.Board).get(search_word) is not None:
            return redirect(url_for('show_board_history',
                                    g_code=data_Structure.db.session.query(data_Structure.Board).get(search_word).code))
        if search_area == 'Boards' or search_area == 'All':
            if search_word is "":
                results_board = data_Structure.db.session.query(data_Structure.Board).all()
            else:
                results_board = data_Structure.db.session.query(data_Structure.Board).filter(
                    data_Structure.Board.code.contains(search_word) |
                    data_Structure.Board.project_name.contains(search_word) |
                    data_Structure.Board.link.contains(search_word) |
                    data_Structure.Board.version.contains(search_word) |
                    data_Structure.Board.id.contains(search_word) |
                    data_Structure.Board.dateAdded.contains(search_word)  # |
                    #    data_Structure.Board.addedBy.username.contains(search_word)
                ).all()

            results_board = list(set(results_board))
        if search_area == 'User' or search_area == 'All':
            pass
        if search_area == 'Projects' or search_area == 'All':
            if search_word is "":
                results_project = data_Structure.db.session.query(data_Structure.Project).all()
            elif search_word is not "":
                results_project = data_Structure.db.session.query(data_Structure.Project).filter(
                    data_Structure.Project.project_name.contains(search_word) |
                    data_Structure.Project.project_description.contains(search_word)
                    # search_word in str(data_Structure.Project.project_name) |
                    # search_word in str(data_Structure.Project.project_description)

                ).all()
            results_project = list(set(results_project))
            if not results_board and not results_project:
                flash('No results were found', 'warning')
                return render_template('base.html')

        return render_template('table.html', args=results_board, projects=results_project,
                               search_form=searchForm.SearchForm(), search_word=search_word)
    return render_template('start.html', search_form=search_form)


@app.route('/addBoard/', methods=['GET', 'POST'])
@login_required
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
        project = data_Structure.db.session.query(data_Structure.Project).get(new_board.project_name)
        project.project_boards.append(new_board)
        data_Structure.db.session.commit()
        if data_Structure.Board.query.filter_by(code=new_board.code).scalar() is not None:
            # if Board is now available
            flash('Board was successfully added!', 'success')
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
            flash('Project ' + add_project_form.project_name.data + ' already exists!', 'danger')
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

            if str(request.form.get('add_platine')) in 'true':
                return redirect(url_for('add__board'))
            return redirect(url_for('start'))
    return render_template('add_project.html', add_project_form=add_project_form)


def delete_history_all(history):
    for obj in history.data_objects:
        image_to_delete = data_Structure.db.session.query(data_Structure.Files).get(int(obj.id))
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
            dele_board = data_Structure.Board.query.filter_by(code=board_form.code.data).first()
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
    new_history = data_Structure.History(history=history, board_code=board.code)
    if file:
        file_id = id(file.filename)
        filename = secure_filename(str(file_id) + file.filename)

        image_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(image_path)
        file_to_add = data_Structure.Files(history=new_history, file_path=filename)
        data_Structure.db.session.add(file_to_add)

    data_Structure.db.session.add(new_history)

    data_Structure.db.session.commit()
    return redirect(url_for('show_board_history', g_code=board.code))


@app.route('/boardHistory/<g_code>/', methods=['POST', 'GET', ])  # shows board History
def show_board_history(g_code):
    view.logged_user = view.get_logged_user()
    nav.nav.register_element("frontend_top", view.nav_bar())
    tg_board = data_Structure.Board.query.get(g_code)
    add_form = HistoryForm(request.form)
    edit_form = EditHistoryForm(request.form)

    if request.method == 'POST' and add_form.send.data:

        file = request.files.get('file')

        add_board_history(board=tg_board, history=add_form.history.data, file=file)
    elif request.method == 'POST' and edit_form.send_edit.data:
        edit_board_history(board=tg_board, history=edit_form.history.data, history_id=edit_form.history_id.data)
    elif request.method == 'POST' and edit_form.delete.data:
        history = data_Structure.History.query.get(int(edit_form.history_id.data))
        delete_history_all(history)

    if edit_form is not None:
        return render_template('boardHistory.html', g_board=tg_board,
                               history=data_Structure.History.query.filter_by(board_code=g_code).order_by(
                                   data_Structure.History.time_and_date).all()[::-1],
                               add_form=add_form, edit_form=edit_form)
    else:
        return render_template('boardHistory.html', g_board=tg_board,
                               history=data_Structure.History.query.filter_by(board_code=g_code).order_by(
                                   data_Structure.History.time_and_date).all()[::-1],
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
    return render_template('ProjectPage.html', project=project, boards=project.project_boards)  # boards_of_project)


@app.route('/project/delete/image/<project_name>/', methods=['POST'])
@login_required
def delete_project_image(project_name):
    view.logged_user = view.get_logged_user()
    # image_to_delete = data_Structure.db.session.query(data_Structure.Files).get(int(img_id))
    project = data_Structure.db.session.query(data_Structure.Project).get(project_name)
    img_id = project.project_default_image_path
    #img_id = None
    project.project_default_image_path = None
    if img_id is not None:
        os.remove(os.path.join(UPLOAD_FOLDER, img_id.replace('_', '\\')))

    # data_Structure.db.session.remove(image_to_delete)
    data_Structure.db.session.commit()

    return redirect(url_for('show_project', project_name=project_name))


@app.route('/project/edit/image/<project_name>', methods=['POST'])
@login_required
def edit_project_image(project_name):
    view.logged_user = view.get_logged_user()
    project = data_Structure.db.session.query(data_Structure.Project).get(project_name)
    file = request.files.get('new_upfile')
    if file:
        file_id = id(file.filename)
        filename = secure_filename(str(file_id) + file.filename)
        if ".jpg" in filename.lower() or ".jpeg" in filename.lower() or ".bmp" in filename.lower():
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            if project.project_default_image_path is not None:
                os.remove(os.path.join(UPLOAD_FOLDER, project.project_default_image_path))
            project.project_default_image_path = filename
            #print(filename)
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
    image_to_delete = data_Structure.db.session.query(data_Structure.Files).get(int(img_id))
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
    history = data_Structure.db.session.query(data_Structure.History).get(int(history_id))
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
    project_to_delete = data_Structure.db.session.query(data_Structure.Project).get(project_name)

    for board in project_to_delete.project_boards:
        for history in board.history:
            for file in history.data_objects:
                os.remove(os.path.join(UPLOAD_FOLDER, file.file_path))
                data_Structure.db.session.delete(file)

            data_Structure.db.session.delete(history)
        data_Structure.db.session.delete(board)
    data_Structure.db.session.commit()
    if project_to_delete.project_default_image_path is not None:
        os.remove(os.path.join(UPLOAD_FOLDER, project_to_delete.project_default_image_path))
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
    user_to_change = data_Structure.db.session.query(data_Structure.User).filter_by(uid=uid).first()

    new_username = request.form.get('new_username')
    user_to_change.username = new_username
    data_Structure.db.session.commit()
    return redirect(url_for('my_profile'))


@app.route('/my_profile/change/email/<uid>/', methods=['POST'])
@login_required
def change_email(uid):
    user_to_change = data_Structure.db.session.query(data_Structure.User).filter_by(uid=uid).first()

    new_email = request.form.get('new_email')
    user_to_change.email = new_email
    data_Structure.db.session.commit()
    return redirect(url_for('my_profile'))


@app.route('/my_profile/change/password/<uid>/', methods=['POST'])
@login_required
def change_password(uid):
    user_to_change = data_Structure.db.session.query(data_Structure.User).filter_by(uid=uid).first()

    if pbkdf2_sha256.verify(request.form.get('old_password'), user_to_change.password_hashed_and_salted):
        new_password_hash = pbkdf2_sha256.hash(request.form.get('new_password_1'))
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
    user_to_delete = data_Structure.db.session.query(data_Structure.User).get(current_user.uid)
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
        'show_registered_users')+'">Registered Users</a>', 'info')
    return render_template('forgot_password.html')


# Sorry for the dumb user, I could not find a better word for this variable... :D
@app.route('/user_forgot_password/change_password/', methods=['POST'])
@login_required
def user_forgot_change_password():
    logged_user = data_Structure.db.session.query(data_Structure.User).get(current_user.uid)
    dumb_user_id = request.form.get('uid')
    dumb_user = None
    if dumb_user_id:
        dumb_user = data_Structure.db.session.query(data_Structure.User).get(int(dumb_user_id))
    if not dumb_user:
        flash('User does not exist! (UID: ' + str(dumb_user_id) + ')', 'danger')
        return redirect(url_for(user_forgot_password))
    if pbkdf2_sha256.verify(request.form.get('current_user_password'), logged_user.password_hashed_and_salted):
        new_password = pbkdf2_sha256.hash(request.form.get('new_password_1'))
        if pbkdf2_sha256.verify(request.form.get('new_password_2'), new_password):
            dumb_user.password_hashed_and_salted = new_password
            data_Structure.db.session.commit()
            flash('password of '+dumb_user.username+' was changed successfully', 'success')
            return redirect(url_for('start'))
        else:
            flash('The new passwords did not match!', 'danger')
            return redirect(url_for(user_forgot_password))
    else:
        flash(current_user.username + ' your password was not correct!', 'danger')
        return redirect(url_for(user_forgot_password))

@app.route('/component/add/', methods=['GET'])
def add_component():
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template('add_component.html')


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
    app.run(debug=False, port=80)#, host='0.0.0.0')
# app.run(debug=False, port=80, host='0.0.0.0')
