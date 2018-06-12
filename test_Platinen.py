from flask import Flask, url_for
from flask_testing import TestCase
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_nav import register_renderer
import unittest
import os
import datetime

import Platinen
import data_Structure
import nav
import ownNavRenderer

# Use this as output to see whats happening
# print("\n*****\n\n", board_form.code.data, "Board_Form\n\n*****\n")

def assertmsg(msg, response):
    assert msg.lower() in str(response.data).lower()

def assert302(response, target=None):
    assert "302" in response.status
    if target:
        assertmsg(target, response)

class test_platos(TestCase):


    def create_app(self):

        SQLALCHEMY_DATABASE_URI = 'sqlite:///static/Database/test_data.sql'
        data_Structure.app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        data_Structure.app.config['TESTING'] = True
        data_Structure.app.config['BOOTSTRAP_LOCAL_SUBDOMAIN'] = 'test_'

        # test_queries()
        # Bootstrap(data_Structure.app)
        # SQLAlchemy(data_Structure.app)
        # nav.nav_logged_in.init_app(app)
        data_Structure.create_database()
        nav.nav.init_app(data_Structure.app)

        register_renderer(data_Structure.app, 'own_nav_renderer',
                          ownNavRenderer.own_nav_renderer)
        data_Structure.app.secret_key = os.urandom(12)
        nav.login_manager.init_app(data_Structure.app)
        
        return data_Structure.app

    def setUp(self):
        data_Structure.db.create_all()
        test_user = data_Structure.User('test_user_static', "123",
                                        "test_static@test.com")
        data_Structure.db.session.add(test_user)
        data_Structure.db.session.commit()

    def tearDown(self):
        data_Structure.db.session.remove()
        data_Structure.db.drop_all()

    def test_help(self):
        response = self.client.get("/help/")
        assert "200" in response.status

    def test_register_user(self):
        response = self.client.get('/registeruser/')
        assert "200" in response.status
        register_data = dict(password="123", password_again="123",
                             username='test_user', email_adress="test@test.com")
        response = self.client.post('/registeruser/', data=register_data,
                                    follow_redirects=True)
        assert 'User was successfully added!' in str(response.data)
        response = self.client.post('/registeruser/', data=register_data,
                                    follow_redirects=True)
        assert 'User does already exist!' in str(response.data)
        register_data = dict(password="123", password_again="123",
                             username='test_user2', email_adress="test@test.com")
        response = self.client.post('/registeruser/', data=register_data,
                                    follow_redirects=True)
        assert 'There is already somone registered with the same Email adress!' in str(response.data)
        register_data = dict(password="123", password_again="1234",
                             username='passwords_no_match',
                             email_adress="test@test.com")
        response = self.client.post('/registeruser/', data=register_data,
                                    follow_redirects=True)

        assert 'The Passwords do not match!' in str(response.data)

    def test_login(self):
        response = self.client.post('/login/')
        assert "200" in response.status
        l_dict = dict(password="123", username='test_user_static')
        response = self.client.post('/login/', data=l_dict,
                                    follow_redirects=True)
        assert "Hi test_user_static" in str(response.data)
        l_dict = dict(password="123", username='not_exists')
        response = self.client.post('/login/', data=l_dict,
                                    follow_redirects=True)
        assert "User does not exist!" in str(response.data)
        l_dict = dict(password="1234", username='test_user_static')
        response = self.client.post('/login/', data=l_dict,
                                    follow_redirects=True)
        assert "Password was not correct" in str(response.data)

    def test_assign_division(self):
        fname = "assign_division"
        self.test_login()
        response = self.client.get(url_for(fname))
        self.assert200(response)
        data = dict(division="SDI")
        response = self.client.post(url_for(fname), data=data)

    def test_logout(self):
        response = self.client.get('/logout/')
        assert "/login/" in str(response.data)
        l_dict = dict(password="123", username='test_user_static')
        response = self.client.post('/login/', data=l_dict,
                                    follow_redirects=True)

        response = self.client.get('/logout/', follow_redirects=True)
        assert "you were logged out successfully!" in str(response.data)

        response = self.client.post('/logout/')
        assert str(405) in response.status
    
    def test_delete_user(self):
        register_data = dict(password="123", password_again="123",
                             username='test_user',
                             email_adress="test@test.com")
        response = self.client.post('/registeruser/', data=register_data,
                                    follow_redirects=True)
        assert "User was successfully added!" in str(response.data)
        register_data = dict(password="123", password_again="123",
                             username='Guest',
                             email_adress="test_guest@test.com")
        response = self.client.post('/registeruser/', data=register_data,
                                    follow_redirects=True)
        assert 'User was successfully added!' in str(response.data)
        l_dict = dict(password="123", username='test_user_static')
        response = self.client.post('/login/', data=l_dict,
                                    follow_redirects=True)
        assert "Hi test_user_static" in str(response.data)
        user = data_Structure.User.query.filter_by(username="test_user").first()
        guest = data_Structure.User.query.filter_by(username="Guest").first()
        response = self.client.get('/deleteuser/')
        assert "200" in response.status
        del_dict = dict(uid=guest.uid)
        response = self.client.post('/deleteuser/', data=del_dict,
                                    follow_redirects=True)
        assert data_Structure.User.query.get(guest.uid) is None
        assert "User was deleted successfully!" in str(response.data)
        response = self.client.post('/deleteuser/', data=dict(uid=user.uid,
                                                              password="123"),
                                    follow_redirects=True)
        assert "User was deleted successfully!" in str(response.data)

    def test_show_registered_users(self):
        l_dict = dict(password="123", username='test_user_static')
        response = self.client.post('/login/', data=l_dict,
                                    follow_redirects=True)
        assert "Hi test_user_static" in str(response.data)
        response = self.client.get('/registeredusers/')
        assert "200" in response.status

    def test_start(self):
        response = self.client.get('/')
        assert "200" in response.status
        search_dict = dict(search_field="", Selector="All")
        response = self.client.post('/', data=search_dict)
        assert "200" in response.status

    def test_add_board_scripted(self):
        scr_data = {"board_id": "TEST_1",
                    "project": "Test_Project",
                    "version": "2",
                    "status": "working",
                    "result": "Passed",
                    "arg_name": "Test"
                    }
        response = self.client.post("/addboard/scripted/test/",
                                    data=scr_data)
        assert "Success" in str(response.data)
        assert "no" not in str(response.data)
        response = self.client.post("/addboard/scripted/test/",
                                    data=scr_data)
        assert "exists" in str(response.data).lower()
        scr_data['comment'] = "Test_Comment"
        response = self.client.post("/addboard/scripted/test/",
                                    data=scr_data)
        assert "comment was added" in str(response.data).lower()
        scr_data['board_id'] = "TEST_2"
        response = self.client.post("/addboard/scripted/test/",
                                    data=scr_data)
        assert "Success and Comment" in str(response.data)

    def test_add__board(self):
        response = self.client.post(url_for('add__board'))
        assert "302" in response.status
        response = self.client.get(url_for('add__board'))
        self.assert200(response)

        scr_data = {"code": "TEST_2",
                    "name": "Test_Project",
                    "ver" : "1.test"
                    }
        project = data_Structure.Project("Test_Project", "Test_Project_Description", None)
        data_Structure.db.session.add(project)
        data_Structure.db.session.commit()
        response = self.client.post(url_for("add__board"), data=scr_data)
        self.assert200(response)
        assert data_Structure.Board.query.get(scr_data["code"]) is not None
        scr_data = {"code": "TEST_3",
                    "name": "INVALID_PROJECT",
                    "ver": "1"}
        response = self.client.post(url_for("add__board"), data=scr_data, follow_redirects=True)
        self.assert200(response)
        assertmsg("The selected Project does not exist. Inform Admin", response)
        
    def test_show_boards_of_project(self):
        project = data_Structure.Project("Test_Project", "Test_Project_Description", None)
        data_Structure.db.session.add(project)
        data_Structure.db.session.commit()
        response = self.client.get(url_for('show_boards_of_project', project_name="Test_Project"))
        self.assert200(response)
        response = self.client.post(url_for("show_boards_of_project", project_name="INVALID_PROJECT"))
        self.assert200(response)

    def test_add_project(self):
        response = self.client.get(url_for("add_project"))
        assert302(response)
        self.test_login()
        response = self.client.get(url_for("add_project"))
        self.assert200(response)
        response = self.client.post(url_for("add_project"), follow_redirects=True)
        self.assert200(response)
        assertmsg("no project data", response)
        project_data = dict(project_name="TEST_METHODE", project_description="TEST_DESC")
        response = self.client.post(url_for("add_project"), data=project_data, follow_redirects=True)
        self.assert200(response)
        assertmsg(project_data["project_name"], response)
        response = self.client.post(url_for("add_project"), data=project_data, follow_redirects=True)
        self.assert200(response)
        assertmsg("already exists", response)

    # TODO implement test for uploading image

    def test_del_board(self):
        url = url_for("del_board")
        response = self.client.get(url)
        assert302(response, url_for('login'))
        response = self.client.post(url)
        assert302(response, url_for("login"))
        self.test_login()
        response = self.client.get(url)
        self.assert200(response)
        response = self.client.post(url)
        self.assert200(response)
        assertmsg("not exist", response)
        self.test_add__board()
        assert data_Structure.Board.query.get("TEST_2") is not None
        response = self.client.post(url_for("del_board"),
                                    data=dict(code="TEST_2"))
        self.assert200(response)
        assertmsg("success", response)
        assert data_Structure.Board.query.get("TEST_2") is None
        response = self.client.post(url, data=dict(code="TEST_2"))
        self.assert200(response)
        assertmsg("not exist", response)

    def test_show_board_history(self):
        fname = "show_board_history"
        response = self.client.get(url_for(fname, g_code="HALLO", follow_redirects=True))
        # assertmsg("not exist", response)
        assert302(response)
        self.test_add__board()
        response = self.client.get(url_for(fname, g_code="TEST_2"))
        self.assert200(response)
        response = self.client.post(url_for(fname, g_code="TEST_2"))
        self.assert200(response)
        # Add History Form
        form_data = dict(add_history="TEST_HISTORY")
        self.test_login()
        response = self.client.post(url_for(fname, g_code="TEST_2"), data=form_data, follow_redirects=True)
        assertmsg("TEST_HISTORY", response)
        self.assert200(response)

        # Edit History Form
        test_history = data_Structure.History.query.filter_by(history="TEST_HISTORY").first()
        form_data = dict(send_edit="True", history_id=str(test_history.id), history="TEST_EDIT_HISTORY")
        response = self.client.post(url_for(fname, g_code="TEST_2"), data=form_data, follow_redirects=True)
        assertmsg("TEST_EDIT_HISTORY", response)
        self.assert200(response)
        
        # Delete History Form
        form_data = dict(delete="True", history_id=str(test_history.id))
        response = self.client.post(url_for(fname, g_code="TEST_2"), data=form_data, follow_redirects=True)
        self.assert200(response)
        assertmsg("The comment was deleted", response)
        ###
        # There is a Test for deleting all answers in test_answer_board_comment()
        ####

    def test_answer_board_comment(self):
        fname = "answer_board_comment"
        response = self.client.get(url_for(fname))
        assert "405" in str(response.status)
        self.test_add__board()
        form_data = dict(send="True", add_history="TEST_HISTORY")
        self.test_login()
        response = self.client.post(url_for("show_board_history", g_code="TEST_2"), data=form_data)
        test_history = data_Structure.History.query.filter_by(history="TEST_HISTORY").first()
        # up now was creating a comment
        form_data = dict(text="TEST ANSWER")
        response = self.client.post(url_for(fname, parent_id=test_history.id),
                                    data=form_data,
                                    follow_redirects=True,
                                    )
        assertmsg("TEST ANSWER", response)
        self.assert200(response)

        # Here we test the removing of comment childs
        form_data = dict(delete="True", history_id=str(test_history.id))
        response = self.client.post(url_for("show_board_history", g_code="TEST_2"), data=form_data, follow_redirects=True)
        self.assert200(response)
        assertmsg("The comment was deleted", response)
        q = data_Structure.History.query.filter_by(history="TEST ANSWER").all()
        assert [] == q
        assert [] == data_Structure.History.query.all()

    def test_show_project(self):
        fname = "show_project"
        response = self.client.get(url_for(fname, project_name="TEST_PROJECT"))
        assertmsg("was not found", response)
        self.test_add_project()
        response = self.client.get(url_for(fname, project_name="TEST_METHODE"))
        self.assert200(response)
        assertmsg("TEST_METHODE", response)  
        self.test_add__board()
        response = self.client.get(url_for(fname, project_name="Test_Project"))
        self.assert200(response)
        assertmsg("TEST_2", response)

    # TODO: delete_project_image
    # TODO: edit_project_image
    # TODO: upload_avatar
    # TODO: delete_history_image
    # TODO: board_history_add_file
    # TODO: delete_project                
        
    def test_my_profile(self):
        response = self.client.get(url_for("my_profile"))
        assert302(response)
        assertmsg(url_for("start"), response)
        self.test_login()
        response = self.client.get(url_for("my_profile"))
        self.assert200(response)
    
    def test_change_username(self):
        fname = "change_username"
        response = self.client.get(url_for(fname, uid="RANDOM"))
        self.assert405(response)
        self.test_login()
        # we are logged in as l_dict = dict(password="123", username='test_user_static') 
        uid = data_Structure.User.query.filter_by(username="test_user_static").first().uid
        response = self.client.post(url_for(fname, uid=uid), data=dict(new_username="new_username"))
        assert302(response, url_for("my_profile"))
        assert data_Structure.User.query.get(int(uid)).username == "new_username"
        response = self.client.post(url_for(fname, uid=uid), 
                                    data=dict(new_username="new_username"),
                                    follow_redirects=True)
        assertmsg("nothing was changed (your username", response)

    def test_change_email(self):
        fname = "change_email"
        response = self.client.get(url_for(fname, uid="RANDOM"))
        self.assert405(response)
        self.test_login()
        # we are logged in as l_dict = dict(password="123", username='test_user_static') 
        uid = data_Structure.User.query.filter_by(username="test_user_static").first().uid
        response = self.client.post(url_for(fname, uid=uid), data=dict(new_email="test_static_new@test.com"))
        assert302(response, url_for("my_profile"))
        assert "test_static_new@test.com" in data_Structure.User.query.get(int(uid)).email

    def test_change_password(self):
        fname = "change_password"
        response = self.client.get(url_for(fname, uid="RANDOM"))
        self.assert405(response)
        self.test_login()
        # we are logged in as l_dict = dict(password="123", username='test_user_static') 
        uid = data_Structure.User.query.filter_by(username="test_user_static").first().uid
        data = dict(old_password="1234")
        response = self.client.post(url_for(fname, uid=uid), data=data, follow_redirects=True)
        assertmsg("was incorrect", response)
        data["old_password"] = "123"
        data["new_password_1"] = "1234"
        data["new_password_2"] = "12345"        
        response = self.client.post(url_for(fname, uid=uid), data=data, follow_redirects=True)
        assertmsg("did not match", response)
        data["new_password_2"] = "1234"        
        response = self.client.post(url_for(fname, uid=uid), data=data, follow_redirects=True)
        assertmsg("password was changed successful", response)
    
    def test_user_forgot_password(self):
        fname = "user_forgot_password"
        response = self.client.get(url_for(fname))
        assert302(response)
        self.test_login()
        response = self.client.get(url_for(fname))
        self.assert200(response)

    def test_user_forgot_change_password(self):
        fname = "user_forgot_change_password"
        dumb = data_Structure.User("DUMB", "1234", "dumb@dumb.com")
        data_Structure.db.session.add(dumb)
        data_Structure.db.session.commit()
        self.test_login()
        uid = data_Structure.User.query.filter_by(username="test_user_static").first().uid
        data = dict(username="NOT_EXIST")
        response = self.client.post(url_for(fname), data=data, follow_redirects=True)
        assertmsg("does not exist", response)
        data["username"] = "DUMB"
        data["current_user_password"] = "1234"
        response = self.client.post(url_for(fname), data=data, follow_redirects=True)
        assertmsg("was not correct", response)
        data["current_user_password"] = "123"
        data["new_password_1"] = "1234"
        data["new_password_2"] = "12345"
        response = self.client.post(url_for(fname), data=data, follow_redirects=True)
        assertmsg("new passwords did not match", response)
        data["new_password_2"] = "1234"
        response = self.client.post(url_for(fname), data=data, follow_redirects=True)
        assertmsg("was changed successfully", response)

    # Line 800 from 1100 - we are getting closer :)
    def test_change_board_version(self):
        fname = "change_board_version"
        response = self.client.get(url_for(fname, board_id="FRAUD"))
        self.assert405(response)
        self.test_login()
        response = self.client.get(url_for(fname, board_id="FRAUD"))
        self.assert405(response)
        self.test_add__board()
        # creates a TEST_2 Board
        c = "test_version"
        b = "TEST_2"
        response = self.client.post(url_for(fname, board_id=b),
                                    data=dict(version_form=c),
                                    follow_redirects=True)
        assertmsg(c, response)
        assertmsg(url_for("show_board_history", g_code=b), response)

    def test_change_board_state(self):
        fname = "change_board_state"
        response = self.client.get(url_for(fname, board_id="FRAUD"))
        self.assert405(response)
        self.test_login()
        response = self.client.get(url_for(fname, board_id="FRAUD"))
        self.assert405(response)
        self.test_add__board()
        # creates a TEST_2 Board
        c = "test_state"
        b = "TEST_2"
        response = self.client.post(url_for(fname, board_id=b),
                                    data=dict(state_form=c),
                                    follow_redirects=True)
        assertmsg(c, response)
        assertmsg(url_for("show_board_history", g_code=b), response)

    # change_board_patch will not be tested since it is deprecated anyway.

    def test_edit_args(self):
        fname = "edit_args"
        response = self.client.get(url_for(fname))
        self.assert405(response)
        self.test_add__board()
        # creates a TEST_2 Board
        data = dict(name="TEST_ARG", board_id="TEST_2", value="TEST_ARG_VAL")
        board = data_Structure.Board.query.get("TEST_2")
        response = self.client.post(url_for(fname, board_id=data["board_id"]),
                                    data=data)
        assert data["name"] in board.args().keys()
        assert data["value"] == board.args()[data["name"]]
        # edit_arg (really edit an existing arg)
        data = dict(name="TEST_ARG", board_id="TEST_2", value="TEST_ARG_VAL_Edited")
        board = data_Structure.Board.query.get("TEST_2")
        response = self.client.post(url_for(fname, board_id=data["board_id"]),
                                    data=data)
        assert data["name"] in board.args().keys()
        assert data["value"] == board.args()[data["name"]]
        # delete arg
        data = dict(name="TEST_ARG", board_id="TEST_2", delete_btn="True")
        response = self.client.post(url_for(fname, board_id=data["board_id"]),
                                    data=data)
        assert data["name"] not in board.args().keys()

    def test_add_device_do(self):
        fname = "add_device_do"
        data = dict(device_name="Test Device", device_brand="Test Brand")
        # correct method
        response = self.client.get(url_for(fname))
        self.assert405(response)
        # add device
        response = self.client.post(url_for(fname), data=data,
                                    follow_redirects=True)
        assertmsg('device \"'+data["device_name"]+'\" was added.', response)

    def test_add_device(self):
        fname = "add_device"
        response = self.client.get(url_for(fname))
        self.assert200(response)

    def test_device_args(self):
        fname = "device_args"
        response = self.client.get(url_for(fname))
        self.assert405(response)
        self.test_add_device_do()
        data = dict(name="Test arg", change_btn="True", value="Test arg value")
        device = data_Structure.Device.query.filter_by(device_name="Test Device").first()
        response = self.client.post(url_for(fname, device_id=device.device_id),
                                    data=data,
                                    follow_redirects=True)
        assertmsg(data["value"], response)
        data = dict(name="Test arg", change_btn="True",
                    value="Test arg value edited")
        response = self.client.post(url_for(fname, device_id=device.device_id),
                                    data=data,
                                    follow_redirects=True)
        assertmsg(data["value"], response)
        data = dict(name="Test arg", delete_btn="True", value="Test arg value")
        response = self.client.post(url_for(fname, device_id=device.device_id),
                                    data=data,
                                    follow_redirects=True)
        assert data["name"] not in device.args().keys()

    def test_show_device(self):
        fname = "show_device"
        self.test_add_device_do() # Creates a "Test Device" Device
        device = data_Structure.Device.query.filter_by(device_name="Test Device").first()        
        response = self.client.get(url_for(fname, device_id=device.device_id))
        self.assert200(response)

    # TODO test_upload_device_document

    def test_delete_device(self):
        fname = "delete_device"
        response = self.client.get(url_for(fname))
        self.assert405(response)
        self.test_add_device_do() # Creates a "Test Device" Device
        device = data_Structure.Device.query.filter_by(device_name="Test Device").first()        
        response = self.client.post(url_for(fname, device_id=device.device_id))
        devices = data_Structure.Device.query.filter_by(device_name="Test Device").all()
        assert302(response)
        assert len(devices) is 0

    def test_add_new_patch(self):
        fname = "add_new_patch"
        response = self.client.get(url_for(fname))
        self.assert405(response)
        self.test_add_project()  # creates a "TEST_METHODE" Project
        project = data_Structure.Project.query.get("TEST_METHODE")
        data = dict(patch_description="TEST Patch")
        response = self.client.post(url_for(fname,
                                            project_id=project.project_name),
                                    data=data,
                                    follow_redirects=True)
        assertmsg("TEST Patch", response)

    def test_edit_patch(self):
        fname = "edit_patch"
        self.test_add_new_patch()  # creates a Patch with "TEST Patch" description
        patch = data_Structure.Patch.query.filter_by(description="TEST Patch").first()
        data = dict(patch_id=patch.patch_id, patch_description="EDITED")
        response = self.client.post(url_for(fname), data=data,
                                    follow_redirects=True)
        assertmsg("Description was changed!", response)
        assertmsg(data["patch_description"], response)

    def test_create_part_type(self):
        fname = "create_part_type"
        response = self.client.get(url_for(fname))
        self.assert200(response)
        data = {"name": "Test_PartType", "input:1": "arg1", "input:2": "arg2"}
        response = self.client.post(url_for(fname), data=data)
        part_type = data_Structure.PartType.query.filter_by(name=data["name"]).first()
        assert "arg1" in part_type.args() and "arg2" in part_type.args()

    def test_show_part_type(self):
        fname = "show_part_type"
        response = self.client.get(url_for(fname))
        self.assert200(response)
        self.test_create_part_type()  # creates a "Test_PartType"
        # with "arg1" and "arg2"
        parttype = data_Structure.PartType.query.filter_by(name="Test_PartType").first()
        data = dict(parttype_id=parttype.id)
        response = self.client.post(url_for(fname), data=data)
        assert302(response)
        response = self.client.get(url_for(fname, parttype_id=parttype.id))
        self.assert200(response)

    def test_remove_part_type_arg(self):
        fname = "remove_part_type_arg"
        self.test_login()
        response = self.client.get(url_for(fname, parttype_id=0))
        self.assert405(response)
        self.test_create_part_type()  # creates a "Test_PartType"
        # with "arg1" and "arg2"
        parttype = data_Structure.PartType.query.filter_by(name="Test_PartType").first()
        data = dict(arg1="arg1")
        response = self.client.post(url_for(fname, parttype_id=parttype.id), data=data)
        assert "arg1" not in parttype.args()
        assert302(response)

    def test_add_part_type_args(self):
        fname = "add_part_type_args"
        self.test_login()
        response = self.client.get(url_for(fname, parttype_id=0))
        self.assert405(response)
        self.test_create_part_type()  # creates a "Test_PartType"
        # with "arg1" and "arg2"
        parttype = data_Structure.PartType.query.filter_by(name="Test_PartType").first()
        data = {"input:1": "arg3"}
        response = self.client.post(url_for(fname, parttype_id=parttype.id), data=data)
        assert "arg3" in parttype.args()
        assert302(response)
        data["input:2"] = "arg4"
        data["input:3"] = "arg5"
        response = self.client.post(url_for(fname, parttype_id=parttype.id), data=data)
        assert "arg4" in parttype.args()
        assert "arg5" in parttype.args()
        assert302(response)
    
    def test_create_part(self):
        fname = "create_part"
        self.test_login()        
        response = self.client.get(url_for(fname))
        self.assert200(response)
        self.test_create_part_type()  # creates a "Test_PartType"
        # with "arg1" and "arg2"
        parttype = data_Structure.PartType.query.filter_by(name="Test_PartType").first()
        response = self.client.get(url_for(fname, parttype_id=parttype.id))
        self.assert200(response)

    def test_create_part_do(self):
        fname = "create_part_do"
        self.test_login()        
        self.test_create_part_type()  # creates a "Test_PartType"
        # with "arg1" and "arg2"
        parttype = data_Structure.PartType.query.filter_by(name="Test_PartType").first()
        data = dict(arg1="Test1", arg2="Test2")
        response = self.client.post(url_for(fname, parttype_id=parttype.id), data=data)
        assert302(response)
        part = data_Structure.Part.query.all()[0]
        assert "Test1" == part.args()["arg1"]
        assert "Test2" == part.args()["arg2"]

    def test_show_part(self):
        fname = "show_part"
        response = self.client.get(url_for(fname))
        self.assert200(response)
        self.test_create_part_do()
        # Test_PartType was created
        part = data_Structure.Part.query.all()[0]
        response = self.client.get(url_for(fname, ids=part.ids))
        self.assert200(response)
    
    def test_edit_part_value(self):
        fname = "edit_part_value"
        response = self.client.post(url_for(fname))
        assert302(response)
        self.test_login()
        self.test_show_part() #Test_PartType and a Test part was created
        part = data_Structure.Part.query.all()[0]        
        response = self.client.get(url_for(fname))
        self.assert405(response)
        data = dict(arg1="TestValue")
        response = self.client.post(url_for(fname, part_ids=part.ids), data=data)
        assert302(response)
        assert data["arg1"] == part.args()["arg1"]

    # upload_part_document - I do not know how to test part documents

    # delete_part_document - if there is no i cannot delete one (see above)

    def test_add_part_comment(self):
        fname = "add_part_comment"
        response = self.client.get(url_for(fname))
        self.assert405(response)
        self.test_login()
        self.test_show_part() #Test_PartType and a Test part was created
        part = data_Structure.Part.query.all()[0]                
        response = self.client.post(url_for(fname, part_ids=part.ids), data=dict(newComment="TestComment"))
        assert302(response)

    # upload_comment_document_part - see above

    def test_edit_comment(self):
        fname = "edit_comment"
        self.test_add_part_comment()
        response = self.client.post(url_for(fname, comment_id="1"), data=dict(edit="edited"), follow_redirects=True)
        assertmsg("Comment was edited!", response)
    
    def test_part_reservation(self):
        fname = "part_reservation"
        self.test_show_part()
        part = data_Structure.Part.query.all()[0]
        data = dict(date=datetime.datetime.now().strftime("%d.%m.%Y"), amount="10")
        response = self.client.post(url_for(fname, part_ids=part.ids), data=data)
        assert302(response)

    def test_delete_part_reservation(self):
        fname = "delete_part_reservation"
        self.test_part_reservation()
        part = data_Structure.Part.query.all()[0]
        data = dict()
        res = part.reservations[0]
        response = self.client.post(url_for(fname, part_ids=part.ids, id=res.id))
        assert302(response)
        assert len(part.reservations.all()) is 0

    def test_add_container(self):
        fname = "add_container"
        self.test_show_part()
        part = data_Structure.Part.query.all()[0]
        data = dict(number=1000)
        response = self.client.post(url_for(fname, part_ids=part.ids), data=data)
        assert302(response)
        assert len(part.containers) > 0

    def test_create_room(self):
        fname = "create_room"
        self.test_login()
        response = self.client.get(url_for(fname))
        self.assert200(response)
        
        data = dict(title="test_room", address="test_address")
        response = self.client.post(url_for(fname), data=data)
        assert len(data_Structure.Room.query.filter_by(title=data["title"]).all()) > 0
        assert302(response)

    def test_show_all_rooms(self):
        fname = "show_all_rooms"
        response = self.client.get(url_for(fname))
        self.assert200(response)
    
    def test_show_room(self):
        fname = "show_room"
        self.test_create_room()
        response = self.client.get(url_for(fname, room_id=1))
        self.assert200(response)

    # TODO: def test_edit_room_property

    def test_add_place(self):
        fname = "add_place"
        self.test_create_room()
        room = data_Structure.Room.query.get(1)
        response = self.client.post(url_for(fname, room_id=room.id))
        assert len(room.places.all()) > 0
        assert302(response)
    
    def test_assign_place(self):
        fname = "assign_place"
        self.test_add_place()
        self.test_add_container()
        part = data_Structure.Part.query.get(1)
        container = data_Structure.Container.query.get(1)
        response = self.client.post(url_for(fname, part_ids=part.ids, container_id=container.id), data=dict(place_id=1), follow_redirects=True)
        assertmsg("Place was assigned", response)


    def test_book_part_reservation(self):
        fname = "book_part_reservation"
        self.test_assign_place()
        self.test_part_reservation()
        part = data_Structure.Part.query.all()[0]
        res = part.reservations[0]
        response = self.client.post(url_for(fname, part_ids=part.ids, id=res.id))
        self.assert200(response)

    def test_take_part(self):
        fname = "take_part"
        self.test_assign_place()
        part = data_Structure.Part.query.all()[0]
        response = self.client.post(url_for(fname, part_ids=part.ids), data=dict(amount="100"))
        self.assert200(response)

    def test_order_part(self):
        fname = "order_part"
        self.test_show_part()
        part = data_Structure.Part.query.all()[0]
        response = self.client.post(url_for(fname, part_ids=part.ids), data=dict(amount="100"))
        assert len(part.orders.all()) > 0        
        
        


        
if __name__ == "__main__":
    unittest.main()