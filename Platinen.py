from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import nav
import data
import data_Structure
import addPlatineForm
import delPlatineForm
import searchForm
from wtforms import validators
import view

app = Flask(__name__)


# data_Structure.db.create_all()

@app.route('/')
def start():
    return render_template('/base.html', search_form=searchForm.SearchForm())


@app.route('/spitout')
def spitOut():
    print(data.query_all_boards())
    return render_template('table.html', args=data.query_all_boards(), search_form=searchForm.SearchForm())


@app.route('/addBoard/', methods=['GET', 'POST'])
def add__board():
    board_form = addPlatineForm.BoardForm(request.form)
    if request.method == 'POST':
        new_board = data_Structure.Board(code=board_form.code.data, project_name=board_form.name.data)
        # print(new_us.username+" "+new_us.email)
        if data_Structure.Board.query.filter_by(code=new_board.code).first() is not None:
            print("Board kann nicht hinzugefügt werden, es ist bereits eines mit dem Selbe identifier vorhanden.")
            redirect(add__board)

        data_Structure.db.session.add(new_board)
        print(data_Structure.db.session.__class__)
        data_Structure.db.session.commit()

        redirect(url_for("spitOut"))

    return render_template('addPlatineForm.html', form=board_form, search_form=searchForm.SearchForm())


@app.route('/deleteBoard/', methods=['GET', 'POST'])
def del_board():
    board_form = delPlatineForm.delBoardForm(request.form)
    if request.method == 'POST':

        if data_Structure.Board.query.filter_by(code=board_form.code.data).first() is None:
            print('Board ist nicht vorhanden, kann also nicht gelöscht werden.')
            redirect(del_board)
        dele_board = data_Structure.Board.query.filter_by(code=board_form.code.data).first()
        data_Structure.db.session.object_session(dele_board).delete(dele_board)
        data_Structure.db.session.commit()
        redirect('/spitout/')
    return render_template('addPlatineForm.html', form=board_form, search_form=searchForm.SearchForm())


@app.route('/search/', methods=['POST', 'GET'])
def search():
    search_form = searchForm.SearchForm(request.form)
    if request.method == 'POST':
        redirect(url_for('show_results'), data_Structure.Board.query.filter_by(search_form.search_value))
    return render_template(request.url_rule, search_form=searchForm.SearchForm())


@app.route('/showResults/', methods=['POST','GET'])
def show_results():
    return render_template('table.html', args=request.form.search_value.data, search_form=searchForm.SearchForm())


if __name__ == '__main__':
    Bootstrap(app)
    SQLAlchemy(app)
    nav.nav.init_app(app)
    app.run(debug=True)
