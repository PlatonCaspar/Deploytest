SQLite format 3   @        
                                                             -�   �    
�� ��                                                                     �R�tableboardboardCREATE TABLE board (
	code VARCHAR(500) NOT NULL, 
	project_name TEXT, 
	link VARCHAR(500), 
	version VARCHAR(20), 
	id INTEGER, 
	"dateAdded" VARCHAR(10), 
	"addedBy" VARCHAR, 
	PRIMARY KEY (code), 
	FOREIGN KEY(project_name) REFERENCES project (project_name), 
	FOREIGN KEY("addedBy") REFERENCES user (username)
))= indexsqlite_autoindex_board_1board�,�/tableprojectprojectCREATE TABLE project (
	project_name TEXT NOT NULL, 
	project_description TEXT, 
	project_default_image_path TEXT, 
	PRIMARY KEY (project_name)
)-A indexsqlite_autoindex_project_1project�3�ItableuseruserCREATE TABLE user (
	username VARCHAR NOT NULL, 
	password_hashed_and_salted VARCHAR, 
	uid INTEGER NOT NULL, 
	email VARCHAR, 
	PRIMARY KEY (username, uid)
)'; indexsqlite_autoindex_user_1user   	   w w                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             ��;KStefan$pbkdf2-sha256$29000$ppSSkhLCmBNiLKXUutcaww$NLRDXl2DqZt.mSC0HfMvjy6Z9nD8Xpw0MVJ5Ys9DwIA猨stefan.steinmueller@siemens.com
   � �                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       	Stefan猨   � �                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                41?FicadFicad is a Platine/static/Pictures/logo.jpg
   � �                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             	Ficad   e �e                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         M=3Test_UserFicad/boardHistory/Test_User/1.2=�04.01.2017 02:21:51GuestJ93017H51DFicad/boardHistory/017H51D/1.1�&�04.01.2017 02:20:28Stefan
   � ��                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           Test_User
	017H51Dn T T                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        �,���@	 �c33017H51DThe board was first created on 04.01.2017 and succeeded every test so far.
Now it should be added by GuestStefanGuest04.01.2017 02:22:3604.01.2017 02:21:03c��� [ 33Test_UserThis History should be created by GuestGuest04.01.2017 02:22:0904.01.2017 02:22:09   ��@	 �!33017H51DThe board was first created on 04.01.2017 and succeeded every test so far.StefanStefan04.01.2017 02:21:1504.01.2017 02:21:03  � �?� ��                                                                     �R�tableboardboardCRE                                                                       �R�tableboardboardCREATE TABLE board (
	code VARCHAR(500) NOT NULL, 
	project_name TEXT, 
	link VARCHAR(500), 
	version VARCHAR(20), 
	id INTEGER, 
	"dateAdded" VARCHAR(10), 
	"addedBy" VARCHAR, 
	PRIMARY KEY (code), 
	FOREIGN KEY(project_name) REFERENCES project (project_name), 
	FOREIGN KEY("addedBy") REFERENCES user (username)
)� += indexsqlite_autoindex_board_1board�,�/tableprojectprojectCREATE TABLE project (
	project_name TEXT NOT NULL, 
	project_description TEXT, 
	project_default_image_path TEXT, 
	PRIMARY KEY (project_name)
)-A indexsqlite_autoindex_project_1project�3�ItableuseruserCREATE TABLE user (
	username VARCHAR NOT NULL, 
	password_hashed_and_salted VARCHAR, 
	uid INTEGER NOT NULL, 
	email VARCHAR, 
	PRIMARY KEY (username, uid)
)'; indexsqlite_autoindex_user_1user      � ��                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 ��tablehistoryhistoryCREATE TABLE history (
	board_code VARCHAR(500), 
	id INTEGER NOT NULL, 
	history TEXT, 
	added_by TEXT, 
	edited_by TEXT, 
	time_and_date VARCHAR(10), 
	last_edited VARCHAR(10), 
	PRIMARY KEY (id), 
	FOREIGN KEY(board_code) REFERENCES board (code)
))= indexsqlite_autoindex_board_1board