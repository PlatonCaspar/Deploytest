from flask import Flask, url_for
from flask_testing import TestCase
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_nav import register_renderer
import unittest
import os

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

    # render_templates = False

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
        #print(data_Structure.User.query.all())

        assert 'The Passwords do not match!' in str(response.data)

    def test_login(self):
        response = self.client.post('/login/')
        assert "200" in response.status
        l_dict = dict(password="123", username='test_user_static')
        response = self.client.post('/login/', data=l_dict,
                                    follow_redirects=True)
        # print(response.data)
        assert "Your Login was succesfull" in str(response.data)
        l_dict = dict(password="123", username='not_exists')
        response = self.client.post('/login/', data=l_dict,
                                    follow_redirects=True)
        assert "User does not exist!" in str(response.data)
        l_dict = dict(password="1234", username='test_user_static')
        response = self.client.post('/login/', data=l_dict,
                                    follow_redirects=True)
        assert "Password was not correct" in str(response.data)

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
        assert "Your Login was succesfull" in str(response.data)
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
        assert "Your Login was succesfull" in str(response.data)
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

    # TODO implement sth for testing "delete_history_all(history)"

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
        
if __name__ == "__main__":
    unittest.main()