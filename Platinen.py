from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import exists, select
import nav
import data
import data_Structure
import addPlatineForm
import delPlatineForm
import searchForm
import messages
import flask_wtf
from wtforms import validators
import view

app = Flask(__name__)


# data_Structure.db.create_all()

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
                                         ver=board_form.ver.data, history= board_form.history.data)

        if data_Structure.Board.query.filter_by(
                code=new_board.code).scalar() is not None:  # check if board already exists
            return render_template('addPlatineForm.html', form=board_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(True, 'board already exists!'))

        data_Structure.db.session.add(new_board)
        data_Structure.db.session.commit()
        if data_Structure.Board.query.filter_by(code=new_board.code).scalar() is not None:
            # if Board is no longer not available
            return render_template('addPlatineForm.html', form=board_form, search_form=searchForm.SearchForm(),
                                   messages=messages.Messages(False, 'Board was succesfully added!'))

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
    print(tg_board.history)

    return render_template('boardHistory.html', g_board=tg_board)


if __name__ == '__main__':
    # app.secret_key = 'Test'
    Bootstrap(app)
    SQLAlchemy(app)
    nav.nav.init_app(app)
    app.run(debug=True)
