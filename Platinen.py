from flask import render_template, request, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_nav import register_renderer
from historyForm import HistoryForm, EditHistoryForm
import nav
import data
import data_Structure
import addPlatineForm
import delPlatineForm
import registerUserForm
import searchForm
import messages
import ownNavRenderer
import os
import deleteUserForm
import project_forms
import time
from passlib.hash import pbkdf2_sha256
from flask_login import login_user, logout_user, login_required, current_user
from data_Structure import app
from werkzeug.utils import secure_filename

import view

nav.login_manager.anonymous_user = data_Structure.User

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '\static\Pictures'
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

            if data_Structure.User.query.filter_by(
                    email=new_user.email).scalar() is not None:  # check if user already exists
                return render_template('registerUserForm.html', form=user_to_register,
                                       search_form=searchForm.SearchForm(),
                                       messages=messages.Messages(True, 'user already exists!'))

            data_Structure.db.session.add(new_user)
            data_Structure.db.session.commit()
            if data_Structure.User.query.filter_by(email=new_user.email).scalar() is not None:
                # if Board is no longer not available
                return render_template('registerUserForm.html', form=user_to_register,
                                       search_form=searchForm.SearchForm(),
                                       messages=messages.Messages(False, 'User was successfully added!'))
        else:
            return render_template('registerUserForm.html', form=user_to_register, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(True, 'The Passwords do not match!'))

    return render_template('registerUserForm.html', form=user_to_register, search_form=searchForm.SearchForm())


@app.route('/logout/')
@login_required
def logout():
    nav.nav.register_element("frontend_top", view.nav_bar())
    logout_user()
    view.logged_user = None
    return redirect(url_for('start'))


@app.route('/login/', methods=['GET', 'POST'])
# @app.route('/login/?next=/<last_page>/', methods=['GET', 'POST'])
def login():
    last_page = request.args.get('next')
    if last_page is None:
        last_page = request.args.get('last_page')
    try:
        url = url_for(last_page)
    except:
        url = None

    nav.nav.register_element("frontend_top", view.nav_bar())
    user_form = registerUserForm.LoginUser(request.form)
    if request.method == 'POST':
        if data_Structure.User.query.filter_by(
                username=user_form.username.data).scalar() is None:  # check if User exists
            return render_template('loginUser.html', form=user_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(True, 'User does not exist!'))
        login_to_user = data_Structure.User.query.filter_by(username=user_form.username.data).first()
        if pbkdf2_sha256.verify(user_form.password.data, login_to_user.password_hashed_and_salted):
            login_user(login_to_user)
        else:
            return render_template('loginUser.html', form=user_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(True, 'Password was not correct!'))
        view.logged_user = login_to_user.username
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
    nav.nav.register_element("frontend_top", view.nav_bar())
    user_form = deleteUserForm.DeleteUser(request.form)
    if request.method == 'POST':
        if data_Structure.User.query.filter_by(
                username=user_form.username.data).scalar() is None:  # check if board already exists
            return render_template('deleteUserForm.html', form=user_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(True, 'User does not exist!'))
        dele_user = data_Structure.User.query.filter_by(username=user_form.username.data).first()
        if pbkdf2_sha256.verify(user_form.password.data, dele_user.password_hashed_and_salted):
            data_Structure.db.session.object_session(dele_user).delete(dele_user)
            data_Structure.db.session.commit()
        else:
            return render_template('deleteUserForm.html', form=user_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(True, 'Password was not correct!'))
        # Skipping the next test because I never needed it until now!
        # if data_Structure.Board.query.filter_by(
        #       code=board_form.code.data).scalar() is not None:  # check if board already exists
        #    return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm(),
        #                          messages=messages.Messages(True, 'Board was not deleted!'))
        if data_Structure.User.query.filter_by(
                username=user_form.username.data).scalar() is None:  # check if User exists
            return render_template('deleteUserForm.html', form=user_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(False, 'User deleted successfully!'))
    return render_template('deleteUserForm.html', form=user_form, search_form=searchForm.SearchForm())


@app.route('/registeredUsers/')
def show_registered_users():
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template('userTable.html', args=data_Structure.User.query.all(), search_form=searchForm.SearchForm())


@app.route('/', methods=['GET', 'POST'])
def start():
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
                    data_Structure.Board.dateAdded.contains(search_word) |
                    data_Structure.Board.addedBy.contains(search_word)).all()

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
                return render_template('base.html', messages=messages.Messages(True, 'No results were found!'))

        return render_template('table.html', args=results_board, projects=results_project,
                               search_form=searchForm.SearchForm(), search_word=search_word)
    return render_template('start.html', search_form=search_form)


@app.route('/showAll/')
def spitOut():
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template('table.html', args=data.query_all_boards(), search_form=searchForm.SearchForm())


@app.route('/addBoard/', methods=['GET', 'POST'])
def add__board():
    nav.nav.register_element("frontend_top", view.nav_bar())
    board_form = addPlatineForm.BoardForm(request.form)
    board_form.name.choices = addPlatineForm.load_choices()
    add_project_form = project_forms.AddProjectForm(request.form)
    if request.method == 'POST':
        new_board = data_Structure.Board(code=board_form.code.data, project_name=board_form.name.data,
                                         ver=board_form.ver.data)
        if data_Structure.Board.query.filter_by(
                code=new_board.code).scalar() is not None:  # check if board already exists
            return render_template('addPlatineForm.html', add_project_form=add_project_form, form=board_form,
                                   search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(True, 'board already exists!'))
        data_Structure.db.session.add(new_board)
        data_Structure.db.session.commit()
        project = data_Structure.db.session.query(data_Structure.Project).get(new_board.project_name)
        project.project_boards.append(new_board)
        data_Structure.db.session.commit()
        if data_Structure.Board.query.filter_by(code=new_board.code).scalar() is not None:
            # if Board is no longer not available
            return render_template('addPlatineForm.html', add_project_form=add_project_form, form=board_form,
                                   search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(False, 'Board was successfully added!'))

        return redirect(url_for("spitOut"))

    return render_template('addPlatineForm.html', add_project_form=add_project_form, form=board_form,
                           search_form=searchForm.SearchForm())


@app.route('/Projects/Boards_belonging_to/<project_name>/', methods=['POST', 'GET'])
def show_boards_of_project(project_name):
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template('table.html', args=data_Structure.Board.query.filter_by(project_name=project_name).all())


@login_required
@app.route('/add_Project/', methods=['POST', 'GET'])
def add_project():
    nav.nav.register_element("frontend_top", view.nav_bar())
    add_project_form = project_forms.AddProjectForm(request.form)
    if request.method == 'POST':
        # check if Project already exists
        if data_Structure.Project.query.get(add_project_form.project_name.data) is not None:
            return render_template('add_project.html',
                                   messages=messages.Messages(True,
                                                              'Project ' +
                                                              add_project_form.project_name.data + ' already exists!'),
                                   add_project_form=add_project_form)
        elif data_Structure.Project.query.get(add_project_form.project_name.data) is None:
            image_path = 'NE'
            if 'upfile' not in request.files:  # //TODO I still need to  check if files are safe
                image_path = None
            file = request.files.get('upfile')
            if file.filename is '':
                image_path = None
            elif file and image_path is 'NE':
                file_id = id(file.filename)
                filename = secure_filename(str(file_id) + file.filename)

                file.save(UPLOAD_FOLDER + '\\' + filename)
                image_path = '/static/Pictures/' + filename

            project_to_add = data_Structure.Project(project_name=add_project_form.project_name.data,
                                                    project_description=add_project_form.project_description.data,
                                                    project_default_image_path=image_path)

            data_Structure.db.session.add(project_to_add)
            data_Structure.db.session.commit()

            print('add_platine ' + str(request.form.get('add_platine')))
            if str(request.form.get('add_platine')) in 'true':
                return redirect(url_for('add__board'))
            return redirect(url_for('start'))
    return render_template('add_project.html', add_project_form=add_project_form)


def delete_history_all(history):
    for obj in history.data_objects:
        image_to_delete = data_Structure.db.session.query(data_Structure.Files).get(int(obj.id))
        # board = data_Structure.db.session.query(data_Structure.board).get(int(board_id))

        os.remove(str(DATA_FOLDER + image_to_delete.file_path.replace('/', '\\')))
        data_Structure.db.session.delete(image_to_delete)
        data_Structure.db.session.commit()
    data_Structure.db.session.delete(history)
    data_Structure.db.session.commit()


@app.route('/deleteBoard/', methods=['GET', 'POST'])
def del_board(board_delete=None):
    nav.nav.register_element("frontend_top", view.nav_bar())
    board_form = delPlatineForm.delBoardForm(request.form)
    if request.method == 'POST':
        if data_Structure.Board.query.filter_by(
                code=board_form.code.data).scalar() is None:  # check if board already exists
            return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(True, 'Board does not exist!'))
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
            return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(True, 'Board was not deleted!'))
        if data_Structure.Board.query.filter_by(
                code=board_form.code.data).scalar() is None and board_delete is None:  # check if board already exists
            return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(False, 'Board was successfully deleted!'))
        if board_delete is not None:
            print(data_Structure.db.session.query(
                data_Structure.Board).get(dele_board.code))
            return
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

        file.save(UPLOAD_FOLDER + '\\' + filename)
        image_path = '/static/Pictures/' + filename
        file_to_add = data_Structure.Files(history=new_history, file_path=image_path)
        data_Structure.db.session.add(file_to_add)

    data_Structure.db.session.add(new_history)

    data_Structure.db.session.commit()
    return redirect(url_for('show_board_history', g_code=board.code))


@app.route('/boardHistory/<g_code>/', methods=['POST', 'GET', ])  # shows board History
def show_board_history(g_code):
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
    nav.nav.register_element("frontend_top", view.nav_bar())
    project = data_Structure.Project.query.get(project_name)
    if project is None:
        return render_template('start.html', messages=messages.Messages(True, 'Project was not found!!'))
    # boards_of_project = data_Structure.Board.query.filter_by(project_name=project_name)
    return render_template('ProjectPage.html', project=project, boards=project.project_boards)  # boards_of_project)


@app.route('/project/delete/image/<img_id>/<project_name>/', methods=['POST'])
def delete_project_image(img_id, project_name):
    # image_to_delete = data_Structure.db.session.query(data_Structure.Files).get(int(img_id))
    project = data_Structure.db.session.query(data_Structure.Project).get(project_name)
    project.project_default_image_path = UPLOAD_FOLDER + '/static/Pictures/logo.jpg'
    if '/static/Pictures/logo.jpg'.replace('/', '_') not in img_id:
        os.remove(str(DATA_FOLDER + img_id.replace('_', '\\')))
    # data_Structure.db.session.remove(image_to_delete)
    # data_Structure.db.session.commit()

    return redirect(url_for('show_project', project_name=project_name))


@app.route('/boardHistory/delete/image/<img_id>/<board_id>/', methods=['POST'])
def delete_history_image(img_id, board_id):
    image_to_delete = data_Structure.db.session.query(data_Structure.Files).get(int(img_id))
    # board = data_Structure.db.session.query(data_Structure.board).get(int(board_id))

    os.remove(str(DATA_FOLDER + image_to_delete.file_path.replace('/', '\\')))
    data_Structure.db.session.delete(image_to_delete)
    data_Structure.db.session.commit()

    return redirect(url_for('show_board_history', g_code=board_id))


@app.route('/boardHistory/add/file/<history_id>/<board_id>', methods=['POST'])
def board_history_add_file(history_id, board_id):
    history = data_Structure.db.session.query(data_Structure.History).get(int(history_id))
    file = request.files.get('new_upfile')
    if file:
        file_id = id(file.filename)
        filename = secure_filename(str(file_id) + file.filename)

        file.save(UPLOAD_FOLDER + '\\' + filename)
        image_path = '/static/Pictures/' + filename
        file_to_add = data_Structure.Files(history=history, file_path=image_path)
        data_Structure.db.session.add(file_to_add)
        data_Structure.db.session.commit()
    return redirect(url_for('show_board_history', g_code=board_id))


@app.route('/project/delete/project/<project_name>/', methods=['POST'])
def delete_project(project_name):
    project_to_delete = data_Structure.db.session.query(data_Structure.Project).get(project_name)

    for board in project_to_delete.project_boards:
        for history in board.history:
            for file in history.data_objects:
                os.remove(DATA_FOLDER + file.file_path)
                data_Structure.db.session.delete(file)

            data_Structure.db.session.delete(history)
        data_Structure.db.session.delete(board)
    data_Structure.db.session.commit()
    if 'logo.jpg' not in project_to_delete.project_default_image_path:
        os.remove(DATA_FOLDER + project_to_delete.project_default_image_path)
    data_Structure.db.session.delete(project_to_delete)
    data_Structure.db.session.commit()
    return redirect(url_for('start'))


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
    app.run(debug=False, host='0.0.0.0', port=50)
