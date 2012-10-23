Tipsy: A Flask Tutorial
======================
[Flask](http://flask.pocoo.org) is a so-called 'microframework' for writing web applications in Python. It's minimalist, and contains nothing but a receptacle in which you might put the components of your kitchen sink. Contrast this with Django, which includes two sinks, a fully-stocked pantry, and a celebrity chef.

This means when we build something with Flask, we have to add everything to the system ourselves. This isn't nearly as hard as it sounds. We'll be using Flask to build a todo-list from the ground up.

Things we will need:

* [Flask](http://flask.pocoo.org)
* [Sqlite](http://www.sqlite.org)
* [Bootstrap](http://twitter.github.com/bootstrap/)
* [Python 2.6-ish](http://www.python.org)

This tutorial is formatted somewhat in the manner of a choose-your-own-adventure. If you're feeling adventurous, you may choose to ignore the supplied hints and strike out on your own as you see fit. 

Chapter 0: In Which We Build Our Git Repository
-----------------------------------------------
A pre-made repository is available for you at http://www.github.com/chriszf/tipsy/. If you choose to use it, fork then clone it. On the other hand, you are welcome to make your own repository from scratch.

Chapter 1: In Which We Think About Things
-----------------------------------------
The approach to this project, according to Zebulon's Grand Unified Theory of Application Development, is to first identify the nouns that make up the model. In this case, we don't have a pre-existing project to extract our nouns from, so we'll have to use our imaginations. We start by identifying 'use cases', or descriptions of how a user interacts with our software. We don't necessarily need to understand all the details at this time, just a high level description to help plan our project.

Since our application is a task list, here are some archetypical use cases:

* A user can log in and view his list
* A user must be able to add a new task
* A user should be able to mark a task as complete

**Take a few minutes to add to this list. It may help to open a new planning document to keep track, since we don't have a tasklist yet.**

From this list, we can identify the following nouns and attributes:

*   **User**
    * id
    * email
    * password
    * name

*   **Task**
    * id
    * title
    * created\_at
    * completed\_at

This is a good starting point, and we can always add more later.

One thing we need to do next is to identify the relationships between our nouns. We can say that a User _has many_ Tasks, and at the same time, a Task _belongs to_ a User.

Chapter 2: In Which We Build Our Database
-----------------------------------------
Now, we almost have enough information to construct our tables. We have our attributes, our nouns, and our relationships, but we still need to declare what column types these attributes will be. Try to do this yourself, and hover over the spoiler block below if you need hints.

<div class="spoilers">
*   **User**
    * id - Integer, Primary Key
    * email - Varchar(64)
    * password - Varchar(64)
    * name - Varchar(64)

*   **Task**
    * id - Integer, Primary Key
    * title - Varchar(64)
    * created\_at - Datetime
    * completed\_at - Datetime
    * user\_id - Integer

Notice the addition of the user\_id field to represent the relation.
</div>

The next thing to do is take our definition and build database tables from it. You can use the [sql diagram tool](http://robotocracy.com/sql/) from before to generate the sql, or use a [sqlite tutorial](http://souptonuts.sourceforge.net/readme_sqlite_tutorial.html) to create the table generation script yourself.

Remember the naming conventions from before: the table name is a capitalized, plural version of the thing it represents.

Save your script in a file named schema.sql. If you need some help, we've provided the script for you here:

<div class="spoilers">
    -- schema.sql

    create table Users (
        id INTEGER PRIMARY KEY,
        email VARCHAR(64),
        password VARCHAR(64),
        name VARCHAR(64)
    );
    create table Tasks (
        id INTEGER PRIMARY KEY,
        title VARCHAR(64),
        created_at DATETIME,
        completed_at DATETIME,
        user_id INTEGER
    );

</div>

Load your sql database using the following command (make sure you're in your repository directory).

    sqlite3 tipsy.db < schema.sql

Chapter 3: In Which We Feed Some Crud to a Snake
------------------------------------------------
We're going to write the [CRUD](http://en.wikipedia.org/wiki/Create,_read,_update_and_delete) access methods to our model, or at least, parts of it. We'll put these methods in a file called model.py.

Generally, when we write database access methods (functions, whatever), we want to start with setup and teardown functions to connect to our database, then shut down the connection cleanly when we're done.

We'll use the setup function from the Flaskr exercise:

    """
    model.py
    """

    import sqlite3

    def connect_db():
        return sqlite3.connect("tipsy.db")

Given a database 'handle', we can make queries against our database. Right now the database is empty, so we need to write a method to put some data in. Although it's not obvious why yet, we need a mechanism to get the id of the most recent data we put in.

    def new_user(db, self, email, password, name):
        c = db.cursor()
        query = """INSERT INTO Users VALUES (NULL, ?, ?, ?)"""
        result = c.execute(query, (email, password, name))
        db.commit()

        return result.lastrowid

If you don't remember the syntax here, review the [sql lesson](https://github.com/chriszf/sql_lesson) before moving on.

Next, we're going to add a function called 'authenticate' which, given a username and password, returns a dictionary of a user's fields pulled from the database, and a _None_ if the credentials do not match. Try to implement this yourself, but feel free to use our reference implementation:

<div class="spoilers">

    def authenticate(db, email, password):
        c = db.cursor()
        query = """SELECT * from Users WHERE email=? AND password=?"""
        c.execute(query, (email, password))
        result = c.fetchone()
        if result:
            fields = ["id", "email", "password", "username"]
            return dict(zip(fields, result))

        return None

    # If you use our implementation, make sure to
    # look up the zip function

</div>

On your own, implement the following methods:

* new\_task(db, title, user\_id) -- Created a new task, returns the id of the newly created row. Make sure to populate the created\_at field.
* get\_user(db, user\_id) -- Fetch a user's record based on his id. Return the user as a dictionary, like our authenticate method.
* complete\_task(db, task\_id) -- Marks a task as being complete, setting the completed\_at field.
* get\_tasks(db, user\_id) -- Gets all the tasks for the given user id. Returns all the tasks in the system if no user\_id is given. Returns them as a list of dictionaries.
* get\_task(db, task\_id) -- Get a single task, given its id. Return the task as a dictionary as above in the authenticate method.
