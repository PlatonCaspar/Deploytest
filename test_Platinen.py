from flask import Flask
from flask_testing import TestCase
import unittest

import Platinen
import data_Structure


class test_platos(TestCase):

    def create_app(self):

        SQLALCHEMY_DATABASE_URI = 'sqlite:///static/Database/test_data.sql'
        data_Structure.app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        data_Structure.app.config['TESTING'] = True
        return data_Structure.app

    def setUp(self):
        data_Structure.db.create_all(True)

    def tearDown(self):
        data_Structure.db.session.remove()
        data_Structure.db.drop_all()

    render_templates = False

    def test_help(self):
        response = self.client.get("/help/")
        self.assert_template_used('help.html')


if __name__ == "__main__":
    unittest.main()