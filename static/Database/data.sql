SQLite format 3   @     7                                                               7 -�   �    	���                                                                                                                                                                                                                                                                                                                                              )= indexsqlite_autoindex_board_1boardz!!�?tableuser_groupuser_groupCREATE TABLE user_group (
	user_type VARCHAR, 
	id INTEGER NOT NULL, 
	PRIMARY KEY (id)
)�_�tableprojectprojectCREATE TABLE project (
	project_name TEXT NOT NULL, 
	project_description TEXT, 
	project_default_image_path TEXT, 
	sub_projects_id TEXT, 
	project_history_id INTEGER, 
	PRIMARY KEY (project_name), 
	FOREIGN KEY(sub_projects_id) REFERENCES project (project_name), 
	FOREIGN KEY(project_history_id) REFERENCES history (id)
)-A indexsqlite_autoindex_project_1project      p p                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      ��KS  TestThis is a simple test project to demonstrate the functionality of this website and the software\static\Pictures\72544432Tulips.jpg
   � �                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          		Test                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 � �r                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      G7317JH4KTest/boardHistory/17JH4K/1R�H03.03.2017 10:18:04719124E53HalloTest/boardHistory/Hallo/1�y�03.03.2017 10:27:4471912448
   � ��                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
17JH4K	Hallo�  n k�� n��                                                                                          �S�tableboardboardCREATE TABLE board (
	code VARCHAR(500) NOT NULL, 
	project_name TEXT, 
	link VARCHAR(500), 
	version VARCHAR(20), 
	id INTEGER, 
	"dateAdded" VARCHAR(10), 
	"addedBy_id" VARCHAR, 
	PRIMARY KEY (code), 
	FOREIGN KEY(project_name) REFERENCES project (project_name), 
	FOREIGN KEY("addedBy_id") REFERENCES user (uid)
)� += indexsqlite_autoindex_board_1boardz!!�?tableuser_groupuser_groupCREATE TABLE user_group (
	user_type VARCHAR, 
	id INTEGER NOT NULL, 
	PRIMARY KEY (id)
)�_�tableprojectprojectCREATE TABLE project (
	project_name TEXT NOT NULL, 
	project_description TEXT, 
	project_default_image_path TEXT, 
	sub_projects_id TEXT, 
	project_history_id INTEGER, 
	PRIMARY KEY (project_name), 
	FOREIGN KEY(sub_projects_id) REFERENCES project (project_name), 
	FOREIGN KEY(project_history_id) REFERENCES history (id)
)-A indexsqlite_autoindex_project_1project   u � u�uu                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         ����p	%�; A 		asdasdqweqwe$pbkdf2-sha256$29000$VUpJKcX4vzdGCEHI2VsL4Q$wgNOCkXnzJ97E1swK92n436cODSGSII6VmQOs72BpOMtest123456789456@google.de    	�; / 	Guest$pbkdf2-sha256$29000$zrm3ljJGSGktJQRgLKVUKg$5XuwJfO86cAxYEkEKuZiccRkoaOdI77nbAVd55KZEqotest123@google.des�ƭ@	�; ) 	Guest$pbkdf2-sha256$29000$zvkfo1RK6f1/j3GOkbK2dg$Q2RkBRT6GCuYw/ZDdFC.1f7XxBmkHAqDf.Gp2e7Nf4gtest@google.de   � 	3�; K ���� 	�; K 		Stefan$pbkdf2-sha256$29000$hvBey5mztvbe.59z7j3nXA$cnb4NjjtbBxzo5mXSCdaFE6u5miw34jTPuZ1qenNdsEstefan.steinmueller@siemens.com    U �p� U                                                                     �:�KtablehistoryhistoryCREATE TABLE history (
	board_code VARCHAR(500), 
	id INTEGER NOT NULL, 
	history TEXT, 
	edited_by_id TEXT, 
	time_and_date VARCHAR(10), 
	last_edited VARCHAR(10), 
	PRIMARY KEY (id), 
	FOREIGN KEY(board_code) REFERENCES board (code), 
	FOREIGN KEY(edited_by_id) REFERENCES user (uid)
)�[�tablefilesfiles
CREATE TABLE files (
	id INTEGER NOT NULL, 
	file_path TEXT, 
	description TEXT, 
	belongs_to_history_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(belongs_to_history_id) REFERENCES history (id)
)�b�'tableuseruserCREATE TABLE user (
	username VARCHAR, 
	password_hashed_and_salted VARCHAR, 
	uid INTEGER NOT NULL, 
	email VARCHAR, 
	user_group INTEGER, 
	is_active BOOLEAN, 
	is_authenticated BOOLEAN, 
	PRIMARY KEY (uid), 
	FOREIGN KEY(user_group) REFERENCES user_group (id), 
	CHECK (is_active IN (0, 1)), 
	CHECK (is_authenticated IN (0, 1))
))= indexsqlite_autoindex_board_1board      v�                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          7��� a/static/Pictures/73982792Chrysanthemum.jpgNone
��   N@ �/static/6�ġp _/static/Pictures/80688808459120027_sd.pdfNone
��      77                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   k���@! c���@! e 330455654564We want to add a new comment to this Board:)02.03.2017 15:16:4602.03.2017 15:16:46   a! W 330455654564Here it comes, the first comment<br>02.03.2017 01:53:2202.03.2017 01:53:22