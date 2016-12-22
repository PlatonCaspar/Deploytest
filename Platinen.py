from flask import Flask, render_template, request, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_nav import register_renderer
from sqlalchemy.sql.expression import exists, select
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
from passlib.hash import pbkdf2_sha256
import flask_wtf
import view

app = Flask(__name__)


# data_Structure.db.create_all()
def is_logged_in():
    if session.get('logged_in'):
        return True
    else:
        return False


@app.route('/registerUser/', methods=['GET', 'POST'])
def register_user():
    user_to_register = registerUserForm.RegisterUser(request.form)
    if request.method == 'POST':
        if user_to_register.password.data == user_to_register.password_again.data:
            new_user = data_Structure.User(username=user_to_register.username.data,
                                           password=user_to_register.password.data,
                                           email=user_to_register.email_adress.data)
            print("the fucking pw are the same!")
            if data_Structure.User.query.filter_by(
                    email=new_user.email).scalar() is not None:  # check if user already exists
                return render_template('registerUserForm.html', form=user_to_register,
                                       search_form=searchForm.SearchForm(),
                                       messages=messages.Messages(True, 'user already exists!'))
            print("i will commit!")
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


@app.route('/deleteUser/', methods=['GET', 'POST'])
def delete_user():
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
    return render_template('userTable.html', args=data_Structure.User.query.all(), search_form=searchForm.SearchForm())


@app.route('/')
def start():
    return render_template('start.html', search_form=searchForm.SearchForm())


@app.route('/spitout/')
def spitOut():
    return render_template('table.html', args=data.query_all_boards(), search_form=searchForm.SearchForm())


@app.route('/addBoard/', methods=['GET', 'POST'])
def add__board():
    board_form = addPlatineForm.BoardForm(request.form)
    if request.method == 'POST':
        new_board = data_Structure.Board(code=board_form.code.data, project_name=board_form.name.data,
                                         ver=board_form.ver.data, history=board_form.history.data)

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


@app.route('/deleteBoard/', methods=['GET', 'POST'])
def del_board():
    board_form = delPlatineForm.delBoardForm(request.form)
    if request.method == 'POST':
        if data_Structure.Board.query.filter_by(
                code=board_form.code.data).scalar() is None:  # check if board already exists
            return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(True, 'Board does not exist!'))
        dele_board = data_Structure.Board.query.filter_by(code=board_form.code.data).first()
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


@app.route('/search/', methods=['POST', 'GET'])
def search():
    search_form = searchForm.SearchForm(request.form)
    if request.method == 'POST':
        redirect(url_for('show_results'), data_Structure.Board.query.filter_by(search_form.search_value))
    return render_template('base.html', search_form=searchForm.SearchForm())


@app.route('/showResults/', methods=['POST', 'GET'])
def show_results():
    return render_template('table.html', args=request.form.search_value.data, search_form=searchForm.SearchForm())


@app.route('/boardHistory/<g_code>/', methods=['POST', 'GET', ])  # shows board History
def show_board_history(g_code):
    tg_board = data_Structure.Board.query.filter_by(code=g_code).first()
    addPlatineForm.ChangeBoard().history.data = 'Test'
    return render_template('boardHistory.html', g_board=tg_board, form=addPlatineForm.ChangeBoard())


if __name__ == '__main__':
    # app.secret_key = 'Test'
    Bootstrap(app)
    SQLAlchemy(app)
    nav.nav.init_app(app)
    register_renderer(app, 'own_nav_renderer', ownNavRenderer.own_nav_renderer)
    app.secret_key = os.urandom(12)
    app.run(debug=True)
