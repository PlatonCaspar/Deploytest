# Platos

## **Platos is a Flask based web application to register, and Comment Boards of Projects.**
(in the Future it will also take care of the components and whatever has to do with organizing them),


## Search Syntax:
For easy use there were a few commands implemented that can be used to make your search more concrete:

### the "and" operator:
if you want both search terms to apply, add a "&" between them like:
    
```
search_term_one&search_term_two 
```


and you will only get results matching both terms

### the assignment operator:
if you want only the boards with the owner attribute and the value "Stefan"
(so all the boards that are with Stefan) assign the value to the attribute with a colon (and no spaces)

```
owner:stefan
```
or e.g.:
```
state:damaged
```

you will only get results with the exact attribute and its value (not case sensitive though)

### combining the
Combining both search operators is also possible:

```
owner:stefan&state:working
```
will return all working boards in stefans possession (they are possessed :) ) 





 
## How does this work:
1. You have to register as an User to make any changes
    1. The Passwords are saved encrypted and not in plain tex but if you dont use HTTPS they are send in plain text (i guess?)
2. Create a new project (Even with a logo as picture)
3. Now you can create Boards and assosiate them with the project
4. On every single board you can now write comments. To every comment you can attach pictures or any other files like an Excel spreadsheet with measurement values to be used in the future. 
5. If you - after a long long time - now find a board, you can search either for its project and get a short description of what it is for or you can check if there were any errors with this board or it was destroyed during some stresstest or whatever.

*If someone lost his or her password, they just have to find someone who did not so that person can change the password for them under [/userforgotpassword/](http://platos.sdi.site/userforgotpassword/ "Click here to change the pasword of someone")*



### Register
* click on the login button in the navbar (submenu from "Hello Guest")
* click the Register button on the login page
* enter your username, email and password
* hit the register button 
 
Done.

### Login
* click on the login button in the navbar (submenu from "Hello Guest")
* enter your username and password
* hit login

Done.

### Create new project
* you need to be logged in!
+ Open the Project submenu in the Navbar
+ click on the "New Project" link
+ you are now on the New Project site
+ enter the name of the project in the intended field
+ enter a short description 
+ "- optional -" select a picture related to the project as project picture
+ hit create

Done.

### Create a new Board
+ open the Board submenu in the navbar
+ click on the "New Board" link
+ you are now on the New Board site
+ enter the Code of the Board
  + the Code is the Identifier, it has to be unique. (The software will tell you if it already exists)
  + the code should be formatted like cccN where 
    + c is a single capital character
    + the three characters should be somehow related to your project like:
    GL1 for the Gridlink1 project or TAP for the TAPAS project
    + N is a number (not only one number but sth like 1 or 10 or 100)
    + it is best to increment the number
+ select the Project the board is related to
    + if you missed creating the board:
        + click on the "+" (plus) button below the select field fill out the appearing form
        + restart with teh process of creating the board
+ enter the version number of the board => it is recommended to start with version "0"
+ hit Create

Done.

### A Project
A Project is an object with a name, description and relationships to boards.
Those attributes are visible on its Project page.
To visit a Project follow those steps:
+ Open the Project submenu in the navbar
+ click "All Projects" 
+ click on the Project you want.

--- OR ---

+ Enter the name of the project in the search field (navbar or start page)
+ --optional-- select "Projects" in the select field of the search field (only navbar search form)
+ hit search button (or enter)
+ select the project you want.

Done.

### A Board
A Board is an object with a code, a related project, a state, version, patch, user defined attributes and comments
Those attributes are visible on its Board page.
To visit a Board follow those steps:
+ via Project Page:
    + open the page of the boards project
    + select the board from the table on this page

+ via search
    + if you know the exact code of the board just enter it into the search field (case sensitiv)
    + hit enter or search button
    + you will be redirected to the board page

    + if you do not know the exact code
        + enter what you know into the search field
        + select the board on the result table

#### Comment
A comment is an object with a related board, its text, time and date (although the time is from another tomezone right now), referrer to the last person making any change and attached documents

To create a comment follow those steps:
+ visit the Board page
+ click the new command button (a speec bubble in the middle next to the Board Comments heading)
+ enter the text you want (markdown will be supported in the future)
+ click "Add comment"
-- optional --
Attaching files to a comment
+ click on the paperclip button on the upper left of the comment
+ select whatever you want to upload 
+ repeat as much as you like

+ To edit a comments text click on the red Edit button on the right bottom corner of the commment
+ hit edit or delete (you will not be asked to confirm anything. it will be executed!)  
