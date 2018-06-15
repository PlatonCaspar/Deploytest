# Platos

## **Platos is a Flask based web application to register, and Comment Boards of Projects.**
(in the Future it will also take care of the components and whatever has to do with organizing them),

## whats new:
<!-- TODO -->
*end of june 2018:*
## Parts
Platos now contains a Part table. The concept behind this is:
* A Part inherits its attributes from its respective PartType!
* Each part has its **IDS** as unique identifier.
* Each single piece of a part is stored in containers. (eg. a Wheel)
* Each wheel can be stored in a place
* The amount of available parts depends on the parts stored in its containers!

### Create a PartType
1. You need to be logged in!
2. Click on the New Submenu and select New PartType
3. Enter the name for the PartType (e.g. Resistor)
4. Enter its first attribute
5. for more attributes hit the "plus" button and a new input field will appear for the next attribute 
6. Repeat 5 as much as you like
7. Hit Create.

Done.

### Creat a Part
1. You need to be logged in!
2. Click on the New Submenu and select New Part
3. Select the PartType for the new Part (if it does not exist: see "Create a PartType")
4. You will see a Form with fields for each attribute defined by its PartType. 
5. Enter the Values for each attribute
6. Hit Submit
7. You will be redirected to the new Part page.

Done.

After creating a Part, there are no containers available for this. If you already have containers ready, create a new one for this part.
If you want to store the container in a specific place, you have to make sure, that this place does already exist.

### Create a Room
Each place lives in a Room that has nothing more but a name and an Address.
1. You need to be logged in!
2. Click on the New Submenu and select New Room
3. Enter the title and the Address of the Room
4. Hit Create
5. You will be redirected to the Room. (Create your places here!)

Done.

### Create a Place
Each place lives in a Room that has nothing more but a name and an Address.
1. You need to be logged in!
2. Go to the Room you want to create the place
3. Hit Add Place
4. Take the label from the Printer and apply it to the place so it will be found again!

Done.

### Assign a Place
1. You need to be logged in!
2. go to the part page of the container you want to assign the place
3. enter the place id for the respective place in the form for the container

Done.

### Reserve a single part
1. You need to be logged in!
2. Go to the page of the Part you want to make the reservation
3. enter the amount you need in the reservation form
4. enter the date you need the parts
5. hit Reserve

if you want to delete the reservation, you can do this on the part page within the "reservations" table. Just hit the red X button for the reservation and it will be removed.

### Book a single reservation
1. You need to be logged in!
2. Go to the page of the Part you want to book the reservation
3. look for your reservation in the "reservations" table
4. hit the green button 
5. **You will be redirected to a Page that shows you the place of the container containg your parts**
6. **Save this page or remember it correct, the Information will be gone after you hit continue**

Done.

### Take some pieces of a part
1. You need to be logged in!
2. Go to the page of the Part you want to take the pieces
3. enter the amount you want to take
4. Hit the "Take" button
5. **You will be redirected to a Page that shows you the place of the container containg your parts**
6. **Save this page or remember it correct, the Information will be gone after you hit continue**

Done.

### Order Parts
The Process of ordering needs 3 major steps.
#### First
1. You need to be logged in!
2. Go to the page of the Part you want to make an order
3. enter the amount to order
4. Hit the "Order" Button
#### Second
1. You need to be logged in!
2. Click on the "Advanced" submenun on the navbar and select "orders"
3. you will see two collapsed panels:
    * Pending orders - all orders that are ordered but not delivered
    * New orders - all orders that are required but not ordered yet
4. Open the "New Orders" panel 
5. Go to the order you just created
6. Now you need to take the official Siemens way to order the part, after that enter the amount you really ordered and hit the green button
7. The order is now listed under "Pending Orders"
#### Third
1. If the order is delivered, open the "Pending Orders" Tab, enter the amount that was delivered and hit the green button.
2. The order will dissapear (or the remaining parts stay pending)
3. Add the new container to the part or update the containers amount


### Reserve Parts from a Projects BOM
#### First
1. You need to be logged in!
2. Go to the Peoject page
3. make sure to upload a valid BOM (from eagle, as csv)
4. if some EXB Parts are not created yet, the upload will fail.
5. so make sure, all parts are already created
6. Enter the number of assemblies you want to reserve parts for
7. enter the date where you need the parts
8. Hit the green Button
#### Second

*if You go to your Profile and open the Processes Panel, you will see all of your Project related Processes. 
If a Process is still a reservation, you can change the Date and also the number of assemblies here.*

Done.

### Book a Projects Reservation
1. Go to your Profile Page
2. open the Process Panel
3. Select the proper Process
4. Hit the Book Button.
    => Booking will fail if there are too less parts in stock. If so, you will either have to change the number of assemblies or order the missing parts.
5. After you booked the Reservation, a File is created in which the Place for each needed container is written.
6. Download that file and take the containers out of its places. They will automatically be removed from its place after you booked the Projects process.

____
-- older --
### Mentions:
Now you can tag another user in a Comment (or answer) with using the "@" operator. 
e.g.:
writing
```
@Stefan
```
within a comment will trigger a notification at Stefans Notification center and he will be redirected to that comment whrn clicking on that Notification

### Markdown support:
Every Comment, and also every Patch description can now be formatted using the [Markdown Syntax](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)







 
## Getting Started:
1. You have to register as an User to make any changes
    1. The Passwords are saved encrypted and not in plain tex but if you dont use HTTPS they are send in plain text (i guess?)
2. Create a new project (Even with a logo as picture)
3. Now you can create Boards and assosiate them with the project
4. On every single board you can now write comments. To every comment you can attach pictures or any other files like an Excel spreadsheet with measurement values to be used in the future. 
5. If you - after a long long time - now find a board, you can search either for its project and get a short description of what it is for or you can check if there were any errors with this board or it was destroyed during some stresstest or whatever.

*If someone lost his or her password, they just have to find someone who did not so that person can change the password for them under [/userforgotpassword/](http://platos.internal.sdi.tools/userforgotpassword/ "Click here to change the pasword of someone")*



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
+ Open the New submenu in the Navbar
+ click on the "New Project" link
+ you are now on the New Project site
+ enter the name of the project in the intended field
+ enter a short description 
+ "- optional -" select a picture related to the project as project picture
+ hit create

Done.
_______________
### Create a new Board
+ open the New submenu in the navbar
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
    + if you missed creating the project:
        + click on the "+" (plus) button below the select field fill out the appearing form
        + restart with teh process of creating the board
+ enter the version number of the board => it is recommended to start with version "0"
+ hit Create

#### NEW:
**From an existing Project, you can now create multiple boards at once. The only requirement is, that there exists already one Board for this project for defining the Project Identifier.**

Done.
___________


### A Project
A Project is an object with a name, description and relationships to boards.
Those attributes are visible on its Project page.
To visit a Project follow those steps:
+ click "Projects" on the navbar 
+ click on the Project you want.

--- OR ---

+ Enter the name of the project in the search field (navbar or start page)
+ --optional-- select "Projects" in the select field of the search field (only navbar search form)
+ hit search button (or enter)
+ select the project you want.

Patches are created and edited on the Project page now and are shown on the related board pages. If a board was patched with a certain patch you just need to activate the patch for that board.

#### NEW:
A Project can now be related to a partlist (BOM). It is therefore possible to make reservations for whole assemblies by one click. Also The Parts are linked to each project which is a good option to share experiences.

Done.
______________
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
A comment is an object with a related board, its text, time and date and a referrer to the last person making any change and attached documents

To create a comment follow those steps:
+ visit the Board page
+ click the new command button (a speech bubble in the middle next to the Board Comments heading)
+ enter the text you want ([Markdown Syntax](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)
 is supported)
+ click "Add comment"
-- optional --
Attaching files to a comment
+ click on the paperclip button on the upper left of the comment
+ select whatever you want to upload 
+ repeat as much as you like

+ To edit a comments text click on the red Edit button on the right bottom corner of the commment (Comments can only be edited by its author)
+ hit edit or delete (you will not be asked to confirm anything. it will be executed!)  
 _______________

## Search
### Search Syntax:
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

### combining the Search Operator
Combining both search operators is also possible:

```
owner:stefan&state:working
```
will return all working boards in stefans possession (they are possessed :) ) 