SQLite format 3   @     :   	                                                            : -��  � ��� �                                                                                                                      �f�#tablehistoryhistoryCREATE TABLE history (
	board_code VARCHAR(500), 
	id INTEGER NOT NULL, 
	history TEXT, 
	edited_by TEXT, 
	time_and_date DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(board_code) REFERENCES board (code)
)��tableboardboardCREATE TABLE board (
	code VARCHAR(500) NOT NULL, 
	project_name VARCHAR(80), 
	link VARCHAR(500), 
	version VARCHAR(20), 
	id INTEGER, 
	"dateAdded" VARCHAR(10), 
	"addedBy" VARCHAR, 
	PRIMARY KEY (code), 
	FOREIGN KEY("addedBy") REFERENCES user (username)
))= indexsqlite_autoindex_board_1board�3�ItableuseruserCREATE TABLE user (
	username VARCHAR NOT NULL, 
	password_hashed_and_salted VARCHAR, 
	uid INTEGER NOT NULL, 
	email VARCHAR, 
	PRIMARY KEY (username, uid)
)'; indexsqlite_autoindex_user_1user      w w                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             ��;KStefan$pbkdf2-sha256$29000$rrW21joHYMw5Z2wNYYyRkg$oupTGy0lRz5zPtXf1D401KvYqM.zuFw6pRD9/gkdt40D�stefan.steinmueller@siemens.com
   � �                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       	StefanD�   � ��s                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           G73StefanHallo9/boardHistory/Stefan/14u�02.01.2017 23:04:59Stefan   �33TestHallo/boardHistory/Test/1e��02.01.2017 22:01:46Gue6-312/boardHistory/1/18�X03.01.2017 00:43:22GuestSQ%C3Test_B53HalloTest/boardHistory/Hallo/1��03.01.2017 02:10:47Guest
   � ���                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
Stefan      1   %	Tes	Hallo   �    	�� 6l �( ��z                      K�߃` [3Stefan<h2>Yo, this seems to Work as well</h2>Guest02.01.2017 22:25:24M�ߔP _3Stefan<h1>Yo, this seems to Work right now</h1>Guest02.01.2017 22:25:24K��� [3Stefan<h2>Yo, this seems to Work as well</h2>Guest02.01.2017 22:25:23M���P _3Stefan<h1>Yo, this seems to Work right now</h1>Guest02.01.2017 22:25:23K�� [3Stefan<h2>Yo, this seems to Work as well</h2>Guest02.01.2017 22:25:21M�� _3Stefan<h1>Yo, this seems to Work right now</h1>Guest02.01.2017 22:25:21K�ߒ0 [3Stefan<h2>Yo, this seems to Work as well</h2>Guest02.01.2017 22:24:30M�߇X _3Stefan<h1>Yo, this seems to Work right now</h1>Guest02.01.2017 22:24:30K�ޔP [3Stefan<h2>Yo, this seems to Work as well</h2>Guest02.01.2017 22:23:30M�މx _3Stefan<h1>Yo, this seems to Work right now</h1>Guest02.01.2017 22:23:30J�ҐX [3Hallo<h2>Yo, this seems to Work as well</h2>Guest02.01.2017 22:22:52L�ғ@ _3Hallo<h1>Yo, this seems to Work right now</h1>Guest02.   ��`   �ߒ0  � g�k! � � � � � � � Z�֑ % m3Test_HistoryÄndeI���p% K3Test_HistoryEtwas neues steht auch am Ende?Guest03.01.2017 01:18:06E�ߒ0  [3<h2>Yo, this seems to Work as well</h2>Guest02.01.2017 22:24:30G�߇X  _3<h1>Yo, this seems to Work right now</h1>Guest02.01.2017 22:24:30E�߃`  [3<h2>Yo, this seems to Work as well</h2>Guest02.01.2017 22:25:24E�ޔP  [3<h2>Yo, this seems to Work as well</h2>Guest02.01.2017 22:23:30G�މx  _3<h1>Yo, this seems to Work right now</h1>Guest02.01.2017 22:23:30�0% m3Test_HistoryÄndere etwas daarn<br>und so ´gehts weiter...Guest03.01.2017 01:11:50� � % m3Test_HistoryÄndere etwas daarn<br>und so ´gehts weiter...Guest03.01.2017 01:11:27� \% g3Test_HistoryÄndere etwas daarn,�֐ % 3Test_HistoryJoGuest03.01.2017 01:31:14G�ғ@  _3<h1>Yo, this seems to Work right now</h1>Guest02.01.2017 22:22:52E�ҐX  [3<h2>Yo, this seems to Work as well</h2>Guest02.01.2017 22:22:52   OP% M3Test_HistoryOkay, jetzt wirds etwas creepy
Guest03.01.2017 01:05:24�  � ��z5 � � � � � � � �                            ^�ҕ % u3Test_HistoryEtwas neues steht auch am Ende? noch was neues?<br>Guest03.01.2017 01:28:34E��`  [3<h2>Yo, this seems to Work as well</h2>Guest02.01.2017 22:25:28G��  _3<h1>Yo, this seems to Work right now</h1>Guest02.01.2017 22:25:21G��P  _3<h1>Yo, this seems to Work right now</h1>Guest02.01.2017 22:25:28 � % 13Test_Historyokay, thats CreepyGuest03.01.2017 01:06:46 �P% K3Test_HistoryAnd here comes the Next HistoryGuest03.01.2017 01:01:34 j % �3Test_HistoryUnd So weiter und so weiter und so geht es immer weiter :)Guest03.01.2017 01:02:26E���  [3<h2>Yo, this seems to Work as well</h2>Guest02.01.2017 22:25:23G���P  _3<h1>Yo, this seems to Work right now</h1>Guest02.01.2017 22:25:23   � % 93Test_HistoryEnter the History hereGuest03.01.2017 01:00:05   _`% m3Test_HistoryÄndere etwas daarn<br>und so ´gehts weiter...Guest03.01.2017 01:12:13G�ߔP  _3<h1>Yo, this seems to Work right now</h1>Guest02.01.2017 22:25:24� 	J �J���:m � � �                                                                                                @���% 93Test_HistoryJo, <h1>som emoer</h1>Guest03.01.2017 02:09:03/���P% 3Test_HistoryHalloGuest03.01.2017 02:07:22� QP% Q3Test_Historyand the newest text is in the top!Guest03.01.2017 01:38:57E��  [3<h2>Yo, this seems to Work as well</h2>Guest02.01.2017 22:25:21E��p  [3<h2>Yo, this seems to Work as well</h2>Guest02.01.2017 22:25:45f %P% g3Test_HistoryÄ>��� % 33T2��  +3HalloHier kommt AlexGuest03.01.2017 02:11:12E��8  [3<h2>Yo, this seems to Work as well</h2>Guest02.01.2017 22:25:27G��p  _3<h1>Yo, this seems to Work right now</h1>Guest02.01.2017 22:25:27G��   _3<h1>Yo, this seems to Work right now</h1>Guest02.01.2017 22:25:26E��8  [3<h2>Yo, this seems to Work as well</h2>Guest02.01.2017 22:25:26    %B���p I3HalloUnd die ist mit loggen in userStefan03.01.2017 02:17:19G��8  _3<h1>Yo, this seems to Work right now</h1>Guest02.01.2017 22:25:45