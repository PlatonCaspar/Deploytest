from data_Structure import Board
#from data_Structure import db
#import data_Structure
#from sqlalchemy import *
#stefan = User(username='Stefan', email='stefan.steinmueller@siemens.com')
#eva = User(username='Eva', email='eva.steinmueller@whatever.com')
#data_Structure.connect_db()
def query_all_boards():
    return Board.query.all()





