from flask import Flask
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
                             username='test_user', email="test@test.com")
        response = self.client.post('/registeruser/', data=register_data,
                                    follow_redirects=True)
        assert 'User was successfully added!' in str(response.data)
        response = self.client.post('/registeruser/', data=register_data,
                                    follow_redirects=True)
        assert 'User does already exist!' in str(response.data)
        register_data = dict(password="123", password_again="123",
                             username='test_user2', email="test@test.com")
        response = self.client.post('/registeruser/', data=register_data,
                                    follow_redirects=True)
        assert 'There is already somone registered with the same Email adress!' in str(response.data)
        register_data = dict(password="123", password_again="1234",
                             username='passwords_no_match',
                             email="test@test.com")
        response = self.client.post('/registeruser/', data=register_data,
                                    follow_redirects=True)
        #print(data_Structure.User.query.all())

        assert 'The Passwords do not match!' in str(response.data)

    def test_login(self):
        print(data_Structure.User.query.all())
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



    


if __name__ == "__main__":
    unittest.main()