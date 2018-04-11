import os
import time
import markdown

from flask import render_template, request, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_login import login_user, logout_user, login_required, current_user
from flask_nav import register_renderer
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256
from werkzeug.utils import secure_filename
from upgrade import migrate_database
from json import dumps

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
import board_labels
import search
import HTTPErrorTable
from data_Structure import app
from historyForm import HistoryForm, EditHistoryForm

nav.login_manager.anonymous_user = data_Structure.User

RELATIVE_PICTURE_PATH = 'static/Pictures'
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), RELATIVE_PICTURE_PATH)
DATA_FOLDER = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


# def set_logged_user(state):
#    logged_user = state

def test_queries():
    with app.app_context():
        migrate_database()

def delete_project():
    pass

@app.errorhandler(500)
def server_error(e):
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template("error.html", error=e, message=HTTPErrorTable.lookup(e)), 500    

@app.errorhandler(404)
def not_found_error(e):
    nav.nav.register_element("frontend_top", view.nav_bar())
    print("**************\n\n{}\n\n*****************".format(e))
    return render_template("error.html",error=e, message=HTTPErrorTable.lookup(e)), 404

@app.errorhandler(405)
def not_found_error(e):
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template("error.html",error=e, message=HTTPErrorTable.lookup(e)), 405

@app.errorhandler(500)
def not_found_error(e):
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template("error.html",error=e, message=HTTPErrorTable.lookup(e)), 500

# This function is called by the autocomplete jquery and returns the user available
@app.route("/mentions/registered/users/score/", methods=['POST'])
@login_required
def get_registered_users():
    """
    "query": "Unit",
    "suggestions": [
        { "value": "United Arab Emirates", "data": "AE" },
        { "value": "United Kingdom",       "data": "UK" },
        { "value": "United States",        "data": "US" }
    ]
    """
    req_str = request.values.get('query').strip('@')
    response_values = []
    for name in current_user.registered_users():
        if name is 'Guest':
            continue
        if req_str in name:
            response_values.append({"value": '@'+name+" ", "data": name})

    return dumps({"query": "Users", "suggestions": response_values})


@app.route('/notifications/clicked/', methods=['POST'])
@login_required
def msg_read():
    msg_id = request.values.get('msg_id')
    try:
        msg = data_Structure.Message.query.get(int(msg_id))
        msg.read = True
        data_Structure.db.session.commit()
    except:
        flash('An error occured in //msg_read()//', 'danger')
    return "200"


@nav.login_manager.user_loader
def load_user(user_id):
    return data_Structure.User.get(user_id)


@app.route('/help/', methods=['GET'])
def help():
    nav.nav.register_element("frontend_top", view.nav_bar())
    # glyphicon glyphicon-question-sign

    input_file = open("readme.md", mode="r", encoding="utf-8")
    text = input_file.read()
    html = "<div class=container>"
    html += markdown.markdown(text)
    html += "</div>"
    input_file.close()
    return render_template('help.html', content=html)


@app.route('/registeruser/', methods=['GET', 'POST'])
def register_user():
    nav.nav.register_element("frontend_top", view.nav_bar())
    user_to_register = registerUserForm.RegisterUser(request.form)
    next = request.values.get('next')
    if request.method == 'POST':
        if user_to_register.password.data == user_to_register.password_again.data:
            new_user = data_Structure.User(username=user_to_register.username.data,
                                           password=user_to_register.password.data,
                                           email=user_to_register.email_adress.data)

            if data_Structure.User.query.filter_by(username=new_user.username).all() != []:
                # check if user already exists
                flash('User does already exist!', 'danger')
                return redirect(url_for('register_user', redir=next))
            if data_Structure.User.query.filter_by(email=new_user.email).all() != []:
                flash('There is already somone registered with the same Email adress!', 'danger')
                return redirect(url_for('register_user', next=next))
            data_Structure.db.session.add(new_user)
            data_Structure.db.session.commit()
            if data_Structure.User.query.filter_by(email=new_user.email).scalar() is not None:
                # if user is no longer not available
                flash('User was successfully added!', 'success')
                return redirect(url_for('login', next=next) or url_for('login'))

        else:
            flash('The Passwords do not match!', 'danger')
            return redirect(url_for('register_user', next=next))

    return render_template('registerUserForm.html', form=user_to_register, search_form=searchForm.SearchForm(), next=next)


@app.route('/logout/')
@login_required
def logout():
    nav.nav.register_element("frontend_top", view.nav_bar())
    logout_user()
    view.logged_user = None
    flash('you were logged out successfully!', 'success')
    return redirect(url_for('start'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    next = request.values.get('next')
    nav.nav.register_element("frontend_top", view.nav_bar())
    user_form = registerUserForm.LoginUser(request.form)

    if request.method == 'POST':
        if 'register_button' in request.form:
                if next:
                    return redirect(url_for('register_user', next=next))
                else:
                    return redirect(url_for('register_user'))
        if user_form.username.data and data_Structure.User.query.filter_by(
                username=user_form.username.data).scalar() is None:  # check if User exists
            flash('User does not exist!', 'danger')
            return render_template('loginUser.html', form=user_form, search_form=searchForm.SearchForm())
        login_to_user = data_Structure.User.query.filter_by(username=user_form.username.data).first()
        if user_form.username.data and pbkdf2_sha256.verify(user_form.password.data, login_to_user.password_hashed_and_salted):
            if request.form.get('rememberMe') is True:
                login_user(login_to_user, remember=True)
                flash('Hi ' + login_to_user.username + ' - Your Login was succesfull', 'success')
            else:
                login_user(login_to_user, remember=False)
                flash('Hi ' + login_to_user.username + ' - Your Login was succesfull', 'success')
        
        else:
            flash('Password was not correct', 'danger')
            return render_template('loginUser.html', form=user_form, search_form=searchForm.SearchForm(), next=next)

            
        return redirect(next or url_for('start'))
       
    return render_template('loginUser.html', form=user_form, search_form=searchForm.SearchForm())


nav.login_manager.login_view = '/login/'  # //TODO I have to define where to redirect when login_required is not okay
nav.login_manager.login_message_category = "info"


@app.route('/deleteuser/', methods=['GET', 'POST'])
@login_required
def delete_user():
    view.logged_user = view.get_logged_user()
    nav.nav.register_element("frontend_top", view.nav_bar())
    user_form = deleteUserForm.DeleteUser(request.form)
    if request.method == 'POST':
        if data_Structure.User.query.get(
                int(user_form.uid.data)) is None:  # check if board already exists
            flash('User does not exist!', 'danger')
            return redirect(url_for('delete_user'))
        dele_user = data_Structure.User.query.get(int(user_form.uid.data))
        if dele_user.username == 'Guest':
            # $.ajax({type:'post', url:'/deleteuser/', data:{'uid':'//enter uid here//', 'password':"abc"}})
            data_Structure.db.session.object_session(dele_user).delete(dele_user)
            data_Structure.db.session.commit()
        elif pbkdf2_sha256.verify(user_form.password.data, current_user.password_hashed_and_salted):
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
        if data_Structure.User.query.get(int(user_form.uid.data)) is None:  # check if User exists
            flash('User was deleted successfully!', 'success')
            return render_template('deleteUserForm.html', form=user_form, search_form=searchForm.SearchForm())
    return render_template('deleteUserForm.html', form=user_form, search_form=searchForm.SearchForm())


@app.route('/registeredusers/')
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
    users = data_Structure.db.session.query(data_Structure.User.username).all()
    if request.method == 'POST':
        if request.form.get('submit_main') is None:
            search_word = request.form.get('search_field')
            search_area = request.form.get('selector')          

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

        if search_area == 'All':
            results_comments = None
            if search_word is not "":
                results_comments = search.search(search_word=search_word, items=data_Structure.History.query.all())
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


@app.route('/addboard/scripted/test/', methods=['POST'])
def add_board_scripted():
    if not request.args:
        request.args = request.form

    board_id = request.args.get('board_id')
    project_name = request.args.get('project')
    ver = request.args.get('version')
    stat = request.args.get('status')
    arg = request.args.get('result')
    arg_name = request.args.get("arg_name")
    comment = request.args.get('comment')
    if not board_id and not project_name and not ver and not stat and not arg:
        return "No Success"
    board = data_Structure.Board.query.get(board_id)
    if board:
        if comment:
            new_comment = data_Structure.History(comment, board_id)
            data_Structure.db.session.add(new_comment)
            data_Structure.db.session.commit()
            return "Comment was added!"
        return "Board Exists"
    else:
        new_board = data_Structure.Board(board_id, project_name, ver)
        new_board.args([arg_name, arg])
        data_Structure.db.session.add(new_board)
        data_Structure.db.session.commit()
        if comment:
            new_comment = data_Structure.History(comment, board_id)
            data_Structure.db.session.add(new_comment)
            data_Structure.db.session.commit()
            return "Success and Comment"
        return "Success"


@app.route('/addboard/', methods=['GET', 'POST'])
def add__board():
    view.logged_user = view.get_logged_user()
    nav.nav.register_element("frontend_top", view.nav_bar())
    board_form = addPlatineForm.BoardForm(request.form)
    board_form.name.choices = addPlatineForm.load_choices()
    add_project_form = project_forms.AddProjectForm(request.form)
    if request.method == 'POST':
        if board_form.code.data is None:
            flash("Some strange error occured\nform.code.data was empty //add__board")
            return redirect(url_for("add__board"))
        if data_Structure.Board.query.filter_by(
                code=board_form.code.data).scalar() is not None:  # check if board already exists
            flash('Board does already exist in the database!', 'danger')
            return redirect(url_for("add__board"))
        if not data_Structure.Project.query.get(board_form.name.data):
            flash("The selected Project does not exist. Inform Admin","danger")
            return redirect(url_for("add__board"))   
            
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
            label_file_cont = board_labels.generate_label(code_number=new_board.code, code_url=url_for('show_board_history', g_code=new_board.code, _external=True))
            board_labels.write_doc(label_file_cont)
            board_labels.print_label("labelprinter01.internal.sdi.tools", "root", "0000")
            return render_template('addPlatineForm.html', add_project_form=add_project_form, form=board_form,
                                   search_form=searchForm.SearchForm())

        return redirect(url_for("start"))

    return render_template('addPlatineForm.html', add_project_form=add_project_form, form=board_form,
                           search_form=searchForm.SearchForm())


@app.route('/projects/boardsbelongingto/<project_name>/', methods=['POST', 'GET'])
def show_boards_of_project(project_name):
    view.logged_user = view.get_logged_user()
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template('table.html', args=data_Structure.Board.query.filter_by(project_name=project_name).all())


@app.route('/addproject/', methods=['POST', 'GET'])
@login_required
def add_project():
    view.logged_user = view.get_logged_user()
    nav.nav.register_element("frontend_top", view.nav_bar())
    add_project_form = project_forms.AddProjectForm(request.form)
    if request.method == 'POST':
        # check if form contains data
        if add_project_form.project_name.data == "" or add_project_form.project_name.data is None:
            flash("No Project data sent. Inform Stefan", "danger")
            return redirect(url_for("add_project"))
        # check if Project already exists
        if data_Structure.Project.query.get(add_project_form.project_name.data) is not None:
            flash('Project ' + add_project_form.project_name.data + ' already exists!', 'danger')
            return render_template('add_project.html', add_project_form=add_project_form)
        elif data_Structure.Project.query.get(add_project_form.project_name.data) is None:
            image_path = 'NE'
            filename = None
            if 'upfile' not in request.files:  # //TODO I still need to  check if files are safe
                image_path = None
            
            else:
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
        image_to_delete = data_Structure.db.session.query(data_Structure.Files).get(int(obj.id))
        # board = data_Structure.db.session.query(data_Structure.board).get(int(board_id))

        os.remove(os.path.join(UPLOAD_FOLDER, image_to_delete.file_path))
        data_Structure.db.session.delete(image_to_delete)
        data_Structure.db.session.commit()
    
    for answer in history.answers:
        delete_history_all(answer)

    data_Structure.db.session.delete(history)
    data_Structure.db.session.commit()


@app.route('/deleteboard/', methods=['GET', 'POST'])
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
                code=board_form.code.data).scalar() is None and board_delete is None:  # check if board no longer exists
            flash('Board was successfully deleted!', 'success')
            return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm())
    return render_template('delBoard.html', form=board_form, search_form=searchForm.SearchForm())


def edit_board_history(board, history_id, history):
    nav.nav.register_element("frontendtop", view.nav_bar())

    history_to_edit = data_Structure.History.query.get(history_id)
    history_to_edit.history = history.replace('\n', "<br>")
    history_to_edit.last_edited = time.strftime("%d.%m.%Y %H:%M:%S")
    history_to_edit.edited_by = data_Structure.db.session.query(data_Structure.User).get(
        data_Structure.User.get_id(current_user))
    data_Structure.db.session.commit()
    history_to_edit.check_mentions()

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


def getSortKeyHistory(h):
    return h.time_date_datetime()


@app.route('/board/show/<g_code>/', methods=['POST', 'GET'])  # shows board History
def show_board_history(g_code):
    view.logged_user = view.get_logged_user()
    nav.nav.register_element("frontend_top", view.nav_bar())
    tg_board = data_Structure.Board.query.get(g_code)
    if not tg_board:
        flash("Board \"{}\" does not exist.".format(g_code), "warning")
        return redirect(url_for('start'))
    add_form = HistoryForm(request.form)
    edit_form = EditHistoryForm(request.form)
    if request.method == 'POST' and request.form.get("add_history"):

        file = request.files.get('file')
        add_board_history(board=tg_board, history=request.form.get("add_history"), file=file)
        return redirect(url_for('show_board_history', g_code=g_code))
    elif request.method == 'POST' and edit_form.send_edit.data:
        edit_board_history(board=tg_board, history=edit_form.history.data, history_id=edit_form.history_id.data)
        return redirect(url_for('show_board_history', g_code=g_code))
        
    elif request.method == 'POST' and edit_form.delete.data:
        history = data_Structure.History.query.get(int(edit_form.history_id.data))
        delete_history_all(history)
        flash("The comment was deleted", "info")
        return redirect(url_for('show_board_history', g_code=g_code))        

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

@app.route('/board/comment/answer/do/', methods=['POST'])
@login_required
def answer_board_comment():
    parent_id = request.args.get('parent_id')
    text = request.form.get('text')
    parent = None
    try:
        parent = data_Structure.History.query.get(int(parent_id))
        parent.add_answer(text)
    except:
        flash('some error occured in //answer_board_comment()//', 'danger')
    finally:
        if parent:
            return redirect(request.referrer or url_for("show_board_history", g_code=parent.board_code))
                
        return redirect(request.referrer or url_for("start"))


@app.route('/project/show/<project_name>/', methods=['POST', 'GET'])
def show_project(project_name):
    view.logged_user = view.get_logged_user()
    nav.nav.register_element("frontend_top", view.nav_bar())
    project = data_Structure.Project.query.get(project_name)
    if project is None:
        flash('Project "' + project_name + '" was not found!', 'danger')
        return render_template('start.html')
    # boards_of_project = data_Structure.Board.query.filter_by(project_name=project_name)
    return render_template('ProjectPage.html', project=project, boards=project.project_boards)  # boards_of_project)

@app.route('/project/show/all/', methods=['GET'])
def show_project_all():
    nav.nav.register_element("frontend_top", view.nav_bar())
    return render_template('table.html', projects=data_Structure.Project.query.all())


@app.route('/project/delete/image/<project_name>/', methods=['POST'])
@login_required
def delete_project_image(project_name):
    view.logged_user = view.get_logged_user()
    # image_to_delete = data_Structure.db.session.query(data_Structure.Files).get(int(img_id))
    project = data_Structure.db.session.query(data_Structure.Project).get(project_name)
    img_id = project.project_default_image_path
    # img_id = None
    project.project_default_image_path = None
    if img_id is not None:
        os.remove(os.path.join(UPLOAD_FOLDER, img_id.replace('_', '\\')))

    # data_Structure.db.session.delete(image_to_delete)
    data_Structure.db.session.commit()

    return redirect(url_for('show_project', project_name=project_name))


@app.route('/project/edit/image/<project_name>/', methods=['POST'])
@login_required
def edit_project_image(project_name):
    view.logged_user = view.get_logged_user()
    project = data_Structure.db.session.query(data_Structure.Project).get(project_name)
    file = request.files.get('new_upfile')
    if file:
        file_id = id(file.filename)
        filename = secure_filename(str(file_id) + file.filename)
        if ".jpg" in filename.lower() or ".jpeg" in filename.lower() or ".bmp" in filename.lower() or ".png" in filename.lower():
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            if project.project_default_image_path is not None:
                os.remove(os.path.join(UPLOAD_FOLDER, project.project_default_image_path))
            project.project_default_image_path = filename
            data_Structure.db.session.commit()
            flash('Picture was changed successfully!', 'success')
        else:
            flash(
                'Your uploaded File was propably not a Picture. Pleas use only PNG(png) JPEG(jpeg) or JPG(jpg) or BMP(bmp) Pictures!',
                'danger')
    return redirect(url_for('show_project', project_name=project_name))


@app.route('/user/profile/avatar/upload/', methods=['POST'])
@login_required
def upload_avatar():
    file = request.files.get('file')

    filename = secure_filename(file.filename)
    if ".jpg" in filename.lower() or ".jpeg" in filename.lower() or ".bmp" in filename.lower() or ".png" in filename.lower():
        current_user.avatar(file)
    else:
        flash(
              'Your uploaded File was propably not a Picture. Pleas use only PNG(png) JPEG(jpeg) or JPG(jpg) or BMP(bmp) Pictures!',
              'danger'
              ) 
    return redirect(url_for('my_profile'))


@app.route('/board/delete/image/<img_id>/<board_id>/', methods=['POST'])
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


@app.route('/board/add/file/<history_id>/<board_id>', methods=['POST'])
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


@app.route('/myprofile/')
@login_required
def my_profile():
    view.logged_user = view.get_logged_user()
    if current_user.username is 'Guest':
        return redirect(url_for('start'))
    nav.nav.register_element("frontend_top", view.nav_bar())

    return render_template('userProfile.html')


@app.route('/myprofile/change/username/<uid>/', methods=['POST'])
@login_required
def change_username(uid):
    user_to_change = data_Structure.db.session.query(data_Structure.User).filter_by(uid=uid).first()
    new_username = request.form.get('new_username')
    if data_Structure.User.query.filter_by(username=new_username).all():
        flash("""Username is already taken, 
             nothing was changed (your username: {})!""".format(user_to_change.username),
             'warning')
        return redirect(request.referrer or url_for('start'))

    user_to_change.username = new_username
    data_Structure.db.session.commit()
    return redirect(url_for('my_profile'))


@app.route('/myprofile/change/email/<uid>/', methods=['POST'])
@login_required
def change_email(uid):
    user_to_change = data_Structure.db.session.query(data_Structure.User).filter_by(uid=uid).first()
    if not user_to_change:
        flash("User does not exist!", "danger")
        return redirect(url_for("start"))
    new_email = request.form.get('new_email')
    user_to_change.email = new_email
    data_Structure.db.session.commit()
    return redirect(url_for('my_profile'))


@app.route('/myprofile/change/password/<uid>/', methods=['POST'])
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


@app.route('/myprofile/delete/me_myself_and_i/and_really_me_so_i_wont_be_able_to_visit_this_site_anymore/',
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


@app.route('/userforgotpassword/', methods=['GET'])
@login_required
def user_forgot_password():
    nav.nav.register_element("frontend_top", view.nav_bar())
    flash('Please enter the uid, you can find it if you look for the user at ' + '<a href="' + url_for(
        'show_registered_users') + '">Registered Users</a>', 'info')
    return render_template('forgot_password.html')



@app.route('/userforgotpassword/change_password/', methods=['POST'])
@login_required
def user_forgot_change_password():
    logged_user = data_Structure.db.session.query(data_Structure.User).get(current_user.uid)
    dumb_user_username = request.form.get('username')
    dumb_user = None
    if dumb_user_username:
        dumb_user = data_Structure.User.query.filter_by(username=dumb_user_username).first()
    if not dumb_user:
        flash('User does not exist! (Username: ' + str(dumb_user_username) + ')', 'danger')
        return redirect(url_for("user_forgot_password"))
    if pbkdf2_sha256.verify(request.form.get('current_user_password'), logged_user.password_hashed_and_salted):
        new_password = pbkdf2_sha256.hash(request.form.get('new_password_1'))
        if pbkdf2_sha256.verify(request.form.get('new_password_2'), new_password):
            dumb_user.password_hashed_and_salted = new_password
            data_Structure.db.session.commit()
            flash('password of ' + dumb_user.username + ' was changed successfully', 'success')
            logout_user()
            return redirect(url_for('start'))
        else:
            flash('The new passwords did not match!', 'danger')
            return redirect(url_for("user_forgot_password"))
    else:
        flash(current_user.username + ' your password was not correct!', 'danger')
        return redirect(url_for("user_forgot_password"))


@app.route('/boardhistory/change/version/<board_id>/', methods=['POST'])
@login_required
def change_board_version(board_id):
    board = data_Structure.Board.query.get(board_id)
    new_version = request.form.get('version_form')
    comment_string = "Version was changed from " + board.version + " to " + new_version
    change_comment = data_Structure.History(comment_string, board.code)
    data_Structure.db.session.add(change_comment)
    board.version = new_version
    data_Structure.db.session.commit()
    return redirect(url_for('show_board_history', g_code=board_id))


@app.route('/boardhistory/change/state/<board_id>/', methods=['POST'])
@login_required
def change_board_state(board_id):
    board = data_Structure.Board.query.get(board_id)
    new_state = request.form.get('state_form')
    comment_string = "State was changed from " + str(board.stat) + " to " + new_state
    change_comment = data_Structure.History(comment_string, board.code)
    data_Structure.db.session.add(change_comment)
    board.stat = new_state
    data_Structure.db.session.commit()
    return redirect(url_for('show_board_history', g_code=board_id))

# deprecated ############################################################
@app.route('/boardhistory/change/patch/<board_id>/', methods=['POST'])
@login_required
def change_board_patch(board_id):
    board = data_Structure.Board.query.get(board_id)
    new_patch = request.form.get('patch_form')
    comment_string = "Patch was changed from " + str(board.patch) + " to " + new_patch
    change_comment = data_Structure.History(comment_string, board.code)
    data_Structure.db.session.add(change_comment)
    board.patch = new_patch
    data_Structure.db.session.commit()
    return redirect(url_for('show_board_history', g_code=board_id))
##########################################################################

@app.route('/upgrade/') # TODO find a way to test flask migrate
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
            code_url=None
            try:
                code_url = url_for('show_device', device_id=device.device_id, _external=True)
            except:
                pass
            label = board_labels.generate_label(device_name, code_url=code_url)
            board_labels.write_doc(label)
            board_labels.print_label("labelprinter01.internal.sdi.tools")
        except:
            flash('An error occured while adding the device to the database', 'danger')
            return redirect(url_for('add_device'))
    
    
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
    try:
        device = data_Structure.Device.query.get(int(request.args.get('device_id')))
    except:
        flash('An error occured //upload_device_document()//', 'danger')
        return redirect(url_for('start'))
    file = request.files['device_documents']
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
        flash("There was no File attached!", "warning")
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
    code_url = None
    if data_Structure.Board.query.get(text):
        code_url = url_for('show_board_history', g_code=text, _external=True)
    
    label = board_labels.generate_label(text, code_url=code_url)
    board_labels.write_doc(label)
    board_labels.print_label(address="labelprinter01.internal.sdi.tools")
    return redirect(url_for('show_new_label'))

@app.route('/project/patch/new/do/', methods=['POST'])
def add_new_patch():
    project = request.args.get('project_id')
    project = data_Structure.Project.query.get(project)
    description = request.form.get('patch_description')
    new_patch = data_Structure.Patch(project)
    new_patch.description = description
    data_Structure.db.session.add(new_patch)
    data_Structure.db.session.commit()
    return redirect(url_for('show_project', 
                            project_name=project.project_name))

@app.route('/project/patch/edit/do/', methods=['POST'])
def edit_patch():
    patch = request.form.get('patch_id')
    patch_description = request.form.get('patch_description')
    try:
        patch = data_Structure.Patch.query.get(int(patch))
    except:
        flash('An error occured //edit_patch()//', 'danger')
        return redirect(url_for('start'))

    patch.description = patch_description
    data_Structure.db.session.commit()
    flash("Description was changed!", 'success')
    
    return redirect(url_for('show_project', project_name=patch.project_id))

@app.route('/project/patch/file/upload/', methods=['POST'])
def patch_add_file():
    
    try:
        patch = request.args.get('patch_id')
        patch = data_Structure.Patch.query.get(int(patch))
    except:
        flash('An error occured //patch_add_file()//', 'danger')
        return redirect(url_for('start'))
    file = request.files['file']
    if file:
        file_id = id(file.filename)
        filename = secure_filename('patchdoc_'+str(file_id) + file.filename)
        

        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        file_to_add = data_Structure.PatchDocument(os.path.join(RELATIVE_PICTURE_PATH, filename))
        data_Structure.db.session.add(file_to_add)
        patch.addFile(file_to_add)
        data_Structure.db.session.commit()
        flash('file was uploaded successful.', 'success')
    else:
        flash('some error occured //patch_add_file()// (no file was sent)', 'warning')

    return redirect(url_for('show_project', project_name=patch.project_id))

@app.route('/project/patch/file/delete/do/', methods=['POST'])
@login_required
def delete_patch_file():
    file_id = request.values.get('file_id')
    try:
        file_ = data_Structure.PatchDocument.query.get(int(file_id))
        file_.delete()
        return "200"
    except:
        flash('some error occured in //delete_patch_file()//', 'danger')
        return "400"


@app.route('/board/patch/check/', methods=['POST'])
def check_patch():
    patch_id = request.args.get('patch_id')
    board_code = request.args.get('board_code')
    
    try:
        patch = data_Structure.Patch.query.get(int(patch_id))
        board = data_Structure.Board.query.get(board_code)
    except:
        flash("An error occured in //check_patch()//", 'danger')
        return redirect(url_for('start'))
    if "check" in request.form:
        try:
            board.patches.append(patch)                    
        except:
            flash("could not append //check_patch()//")
    else:
        try:
            board.patches.remove(patch)
        except:
            flash("Could not remove //check_patch()//")      
        
            
    data_Structure.db.session.commit()
    return redirect(url_for('show_board_history', g_code=board_code))

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

@app.route('/parts/parttype/create/', methods=['GET', 'POST'])
def create_part_type():
    nav.nav.register_element("frontend_top", view.nav_bar())
    if request.method == "GET":
        return render_template('create_part_type.html')
    elif request.method == "POST":
        name = request.form.get('name')
        if name:
            if not data_Structure.PartType.query.filter_by(name=name).scalar():
                part_type = data_Structure.PartType(name)
                data_Structure.db.session.add(part_type)
                data_Structure.db.session.commit()
                for args in request.form:
                    if "input" in args:
                        part_type.args(attr=request.form[args])
                flash("Part Type was created successfull.", "success")
                return redirect(url_for("start"))
            else:
                flash("Part Type is already existing. It will not be created twice!", "warning")
                return redirect(url_for('create_part_type'))
        else:
            flash('Please name the type!', "info")
            return redirect(url_for('create_part_type'))




if __name__ == '__main__':
    # app.secret_key = 'Test'
    test_queries()
    Bootstrap(app)
    SQLAlchemy(app)
    # nav.nav_logged_in.init_app(app)
    data_Structure.create_database()
    nav.nav.init_app(app)

    register_renderer(app, 'own_nav_renderer', ownNavRenderer.own_nav_renderer)
    app.secret_key = os.urandom(12)
    nav.login_manager.init_app(app)
    # login_manager is initialized in nav because I have to learn how to organize and I did not know that im able to
    # implement more files per python file and in nav was enough space.
    
    app.run(debug=False, port=80, host='0.0.0.0')
    

    
# app.run(debug=False, port=80, host='0.0.0.0')
