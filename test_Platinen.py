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

        ## test_queries()
        Bootstrap(data_Structure.app)
        SQLAlchemy(data_Structure.app)
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
        t_user = data_Structure.User('Test_User', 'test', 'test@test.com')
        data_Structure.db.session.add(t_user)
        data_Structure.db.session.commit()

    def tearDown(self):
        data_Structure.db.session.remove()
        data_Structure.db.drop_all()

    #render_templates = False

    def test_help(self):
        response = self.client.get("/help/")
        assert "200" in response.status
    
    # def test_login(self):
    #     response = self.client.post('/logout/')
    #     print(response)
    #     assert ""

    def test_delete_what(self):
        assert ""
    


if __name__ == "__main__":
    unittest.main()