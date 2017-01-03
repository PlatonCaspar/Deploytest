from conda.history import History
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
from passlib.hash import pbkdf2_sha256
from flask_login import login_user, logout_user, login_required, current_user
from data_Structure import app

import view

nav.login_manager.anonymous_user = data_Structure.Anonymous


# def set_logged_user(state):
#    logged_user = state


# data_Structure.db.create_all()
def is_logged_in():
    if session.get('logged_in'):
        return True
    else:
        return False


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


@app.route('/login/?next=/<last_page>/', methods=['GET', 'POST'])
def login(last_page):
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


nav.login_manager.login_view = '/login'


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
                username=user_form.username.data).scalar() is None:  # check if board already exists
            return render_template('deleteUserForm.html', form=user_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(False, 'User deleted successfully!'))
    return render_template('deleteUserForm.html', form=user_form, search_form=searchForm.SearchForm())


@app.route('/registeredUsers/')
def show_registered_users():
    nav.nav.register_element("frontend_top", view.nav_bar())
    print(current_user)
    return render_template('userTable.html', args=data_Structure.User.query.all(), search_form=searchForm.SearchForm())


@app.route('/', methods=['GET', 'POST'])
def start():
    nav.nav.register_element("frontend_top", view.nav_bar())
    search_form = searchForm.SearchForm(request.form)
    if request.method == 'POST':
        search_word = search_form.search_value.data
        if search_word is "":
            return redirect(url_for('spitOut'))
        results = data_Structure.Board.query.filter_by(code=search_word).all()
        results += data_Structure.Board.query.filter_by(project_name=search_word).all()
        results += data_Structure.Board.query.filter_by(link=search_word).all()
        results += data_Structure.Board.query.filter_by(version=search_word).all()
        results += data_Structure.Board.query.filter_by(id=search_word).all()
        results += data_Structure.Board.query.filter_by(dateAdded=search_word).all()
        results += data_Structure.Board.query.filter_by(addedBy=search_word).all()
        results = list(set(results))
        return render_template('table.html', args=results, search_form=searchForm.SearchForm())
    return render_template('start.html', search_form=search_form)


@app.route('/showAll/')
def spitOut():
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template('table.html', args=data.query_all_boards(), search_form=searchForm.SearchForm())


@app.route('/addBoard/', methods=['GET', 'POST'])
def add__board():
    nav.nav.register_element("frontend_top", view.nav_bar())
    board_form = addPlatineForm.BoardForm(request.form)
    if request.method == 'POST':
        new_board = data_Structure.Board(code=board_form.code.data, project_name=board_form.name.data,
                                         ver=board_form.ver.data)
        if data_Structure.Board.query.filter_by(
                code=new_board.code).scalar() is not None:  # check if board already exists
            return render_template('addPlatineForm.html', form=board_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(True, 'board already exists!'))

        data_Structure.db.session.add(new_board)
        data_Structure.db.session.commit()
        if data_Structure.Board.query.filter_by(code=new_board.code).scalar() is not None:
            # if Board is no longer not available
            return render_template('addPlatineForm.html', form=board_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(False, 'Board was successfully added!'))

        return redirect(url_for("spitOut"))

    return render_template('addPlatineForm.html', form=board_form, search_form=searchForm.SearchForm())


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
            image_path = None
            # if add_project_form.project_image.data is not None:
            #    image_data = request.FILES[add_project_form.project_image.name].read()
            #    image_path = '/static/Pictures/' + add_project_form.project_name + '/'
            #    open(os.path.join(image_path, add_project_form.project_image.data), 'w').write(image_data)
            project_to_add = data_Structure.Project(project_name=add_project_form.project_name.data,
                                                    project_description=add_project_form.project_description.data,
                                                    project_default_image_path=image_path)
            print(project_to_add.project_name + '  Picture_Path: ' + str(image_path))
            data_Structure.db.session.add(project_to_add)
            data_Structure.db.session.commit()
            return redirect(url_for('start'))
    return render_template('add_project.html', add_project_form=add_project_form)


@app.route('/deleteBoard/', methods=['GET', 'POST'])
def del_board():
    nav.nav.register_element("frontend_top", view.nav_bar())
    board_form = delPlatineForm.delBoardForm(request.form)
    if request.method == 'POST':
        if data_Structure.Board.query.filter_by(
                code=board_form.code.data).scalar() is None:  # check if board already exists
            return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(True, 'Board does not exist!'))
        dele_board = data_Structure.Board.query.filter_by(code=board_form.code.data).first()
        for history in data_Structure.History.query.filter_by(board_code=dele_board.code).all():
            data_Structure.db.session.object_session(history).delete(history)
            data_Structure.db.session.commit()
        data_Structure.db.session.object_session(dele_board).delete(dele_board)
        data_Structure.db.session.commit()
        if data_Structure.Board.query.filter_by(
                code=board_form.code.data).scalar() is not None:  # check if board already exists
            return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(True, 'Board was not deleted!'))
        if data_Structure.Board.query.filter_by(
                code=board_form.code.data).scalar() is None:  # check if board already exists
            return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(False, 'Board was successfully deleted!'))
    return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm())


def edit_board_history(board, history_id,
                       history):  # //TODO: I Still have to implement the Edit Board History Function.
    nav.nav.register_element("frontend_top", view.nav_bar())
    print(history)
    return redirect(url_for('show_board_history', board.code))


def add_board_history(board, history):
    new_history = data_Structure.History(history=history, board_code=board.code)
    data_Structure.db.session.add(new_history)
    data_Structure.db.session.commit()
    print(new_history.edited_by)

    return redirect(url_for('show_board_history', g_code=board.code))


@app.route('/boardHistory/<g_code>/', methods=['POST', 'GET', ])  # shows board History
def show_board_history(g_code):
    nav.nav.register_element("frontend_top", view.nav_bar())
    tg_board = data_Structure.Board.query.get(g_code)
    add_form = HistoryForm(request.form)
    edit_form = EditHistoryForm(request.form)
    print(request.method)
    if request.method == 'POST' and add_form.send.data:
        print('here we are')
        add_board_history(tg_board, add_form.history.data)
    elif request.method == 'POST' and edit_form.send.data:
        print('I want to Edit')
        edit_board_history(tg_board, edit_form.history_id.data)

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


if __name__ == '__main__':
    # app.secret_key = 'Test'

    Bootstrap(app)
    SQLAlchemy(app)
    nav.nav_logged_in.init_app(app)
    nav.nav.init_app(app)

    register_renderer(app, 'own_nav_renderer', ownNavRenderer.own_nav_renderer)
    app.secret_key = os.urandom(12)
    nav.login_manager.init_app(app)
    # login_manager is initialized in nav because I have to learn how to organize and I did not know that im able to
    # implement more files per python file and in nav was enough space.
    app.run(debug=True)
