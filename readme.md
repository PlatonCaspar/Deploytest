# Platos

## **Platos is a Flask based web application to register, and Comment Boards of Projects.**
 
## How does this work:
1. You have to register as an User to make any changes
    1. The Passwords are saved encrypted and not in plain tex but if you dont use HTTPS they are send in plain text (i guess?)
2. Create a new project (Even with a logo as picture)
3. Now you can create Boards and assosiate them with the project
4. On every single board you can now write comments. To every comment you can attach pictures or any other files like an Excel spreadsheet with measurement values to be used in the future. 
5. If you - after a long long time - now find a board, you can search either for its project and get a short description of what it is for or you can check if there were any errors with this board or it was destroyed during some stress test or whatever.

*If someone lost his or her password, they just have to find someone who did not so that person can change the password for them under [/_user_forgot_password/](https://platos.sdi.site/user_forgot_password/ "Click here to change the pasword of someone")*


### The following libraries are required next to the standard python libs:
+ flask
+ flask_bootstrap
+ flask_sqlalchemy
+ flask_nav
+ passlib
+ flask_login
+ werkzeug
+ flask_wtf
+ wtforms
+ dominate
