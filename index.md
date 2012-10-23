Tipsy: Being a Tutorial on the Ways of Flask
======================
[Flask](http://flask.pocoo.org) is a so-called 'microframework' for writing web applications in Python. It's minimalist, and contains nothing but a receptacle in which you might put the components of your kitchen sink. Contrast this with Django, which includes two sinks, a fully-stocked pantry, and a celebrity chef.

This means when we build something with Flask, we have to add everything to the system ourselves. This isn't nearly as hard as it sounds. We'll be using Flask to build a todo-list from the ground up.

Things we will need:

* [Flask](http://flask.pocoo.org)
* [Sqlite](http://www.sqlite.org)
* [Bootstrap](http://twitter.github.com/bootstrap/)
* [Python 2.6-ish](http://www.python.org)

This tutorial is formatted somewhat in the manner of a choose-your-own-adventure. If you're feeling adventurous, you may choose to ignore the supplied hints and strike out on your own as you see fit, and see what treasures ye may find lurking.

Chapter 0: In Which We Build Our Git Repository
-----------------------------------------------
A pre-made repository is available for you at http://www.github.com/chriszf/tipsy/. It contains most of the code written here, including all of the 'hidden' code in the tutorial. Use it as a reference point, but try to create your own repository and follow along the tutorial.

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

Given a database 'handle', we can make queries against our database. Right now the database is empty, so we need to write a method to put some data in. Although it's not obvious why yet, we need a mechanism to get the id of the most recent data we put in. Look up the _lastrowid_ attribute of cursors in the python sqlite documentation.

    def new_user(db, email, password, name):
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

* **new\_task(db, title, user\_id)** -- Created a new task, returns the id of the newly created row. Make sure to populate the created\_at field.
* **get\_user(db, user\_id)** -- Fetch a user's record based on his id. Return the user as a dictionary, like our authenticate method.
* **complete\_task(db, task\_id)** -- Marks a task as being complete, setting the completed\_at field.
* **get\_tasks(db, user\_id)** -- Gets all the tasks for the given user id. Returns all the tasks in the system if no user\_id is given. Returns them as a list of dictionaries.
* **get\_task(db, task\_id)** -- Get a single task, given its id. Return the task as a dictionary as above in the authenticate method.

As you write these functions, save and commit frequently. Test that your functions work by running your model file with the -i flag:

    Meringue:tipsy chriszf$ python -i model.py 
    >>> db = connect_db()
    >>> bob_id = new_user(db, "bob@loblaw.com", "password", "Bob Loblaw")
    >>> bob_task = new_task(db, "Finish my law blog", bob_id)
    >>> 

When you're done, 'seed' your database with some initial data by writing a small script that imports your model file.

    """
    seed.py
    """
    import model
    
    db = model.connect_db()
    user_id = model.new_user(db, "chriszf@gmail.com", "securepassword", "Christian")
    task = model.new_task(db, "Complete this task list", user_id)

Add as many sample users and tasks as you like, then run your seed.py program to fill your database.

Chapter 4: In Which Our Hero Is Introduced
------------------------------------------
Now, it's time to bring Flask into the mix. There's nothing 'web-specific' about our model code that we've written. We could just as easily have written a command line database app as before, but that's not what we're here for. In our Zugtoad diagrams, the next step is identifying the widget. In this case, it's not our Users, but our Tasks, so we should start by making a view for those (we'll worry about making it novel later).

First, we set up our main application file as follows from the Flask website:

    """
    tipsy.py -- A flask-based todo list
    """
    from flask import Flask, render_template
    import model

    app = Flask(__name__)

    @app.route("/")
    def index():
        return "Woo I'm tipsy"

    if __name__ == "__main__":
        app.run(debug=True)

There's a fair bit of code here, so we'll break it down. The import lines aren't anything special, but notice we imported our model file that we wrote in the last chapter. The next line simply initializes our program to be a Flask application. 

    app = Flask(__name__)

Notice the capital letter, this means Flask is a class. So our app is an instantiation of the Flask class. The first parameter passed to the initializer is the name of the module (file) that we're doing this from. Mostly, you can ignore this detail and do it blindly. In more complex apps, you can use this to make your log messages clearer. We'll skip ahead past the next bit and look at the last lines:

    if __name__ == "__main__":
        app.run(debug=True)

These lines start our application server/web server/flask application when we run our program from the command line. There are times when we want to import our tipsy.py file but _not_ start the server. This is true especially in the case of running tests. We start the server in debug mode to make things simple.

The server, once started, listens for requests from web browsers. When a request comes in, Flask looks at the url asked for by the browser. It then matches the url with any number of 'routes' registered in the application:

    @app.route("/")
    def index():
        return "Woo I'm tipsy"

This is a _decorated function_. The function is named 'index', but we have a 'decorator' above it that tells Flask what url (route) is attached to this function. The exact mechanism it uses to do this is [slightly complicated](http://stackoverflow.com/questions/739654/understanding-python-decorators). Feel free to revisit it at a later date, and trust that it makes this mapping between url and function. Whenever a browser asks for that url from our server, the decorated function (also called a 'view') gets called, and the return value of that function is sent to the browser.

In this case, we are saying the url path "/" (the latter part of 'http://localhost:5000/'), is mapped to the view function named 'index'. When index is called, it returns the string, "Woo I'm tipsy" back to the browser to be displayed. Opena browser and go to [http://localhost:5000/](http://localhost)

If we want to return html, we could modify our 'index' view to be the following:

    @app.route("/")
    def index():
        return "<html><body>Woo I'm tipsy</body></html>"

Try doing this and reloading the page. This, however, is unsustainable. The HTML here is too hard to edit to be useful. Fortunately, we have 'templates', HTML files that have variables we can fill in. If it helps, you can think about templates as mad libs. We'll need a place to put our templates. By default, it needs to be in a directory called 'templates'. We also need a few more directories to make everything fall into place, so we'll go ahead and make those now.

    # Directories that need to be created in our project directory.
    templates/
    static/img/
    static/css/

In the templates directory, we'll put an html file named 'index.html'. This file should contain a well-formed header and body, with a single h1 element in the body that says, "Welcome to Tipsy". The page title should simply be 'Tipsy'. Try it on your own, reviewing Pamela Fox's materials if necessary.

<div class="spoilers">

    <html>
    <head>
        <title>Tipsy</title>
    </head>
    <body>
        <h1>Welcome to Tipsy</h1>
    </body>
    </html>
</div>

Now, we'll change our view to use this template file, using the render\_template function:

    @app.route("/")
    def index():
        return render_template("index.html")

Save all your files, and check your server in the browser to see how your app has changed.

One last thing, remember how we said our template was like a mad lib? Well, right now our template is completely static. We have no way to 'fill in the blanks', so to speak. We don't have any blanks, either. Let's make some now. Modify your index.html file to look like this:

    <html>
    <head>
        <title>Tipsy</title>
    </head>
    <body>
        <h1>Welcome to Tipsy, {{ user_name }}</h1>
    </body>
    </html>

Save it, then reload the page and see what happens.

The output in our browser has a comma, but an empty space where our double-braces enclosed 'user\_name' is. Curious. Let's change our view function one last time.

    @app.route("/")
    def index():
        return render_template("index.html", user_name="chriszf")

Reload the page and behold the magic.

An explanation: in our templates, we can enclose a word with double braces, making it into a variable. This is essentially, in our mad lib analogy, making an empty space in our text and asking for an adverb. In our view, when we render the template, we can fill in that blank by passing in a named argument to the render\_template function. Try changing the name of the argument in the view and the template and seeing how they interact.

Chapter 5: In Which Flask is Introduced to a Model
--------------------------------------------------
We can fill in the empty spaces in our templates with the contents of variables. It stands to reason that we can populate those variables with data from our database. Let's see how that's done. Make a new view named list\_tasks that is attached to the "/tasks" url. It should render a template named "list\_tasks.html" and return the result of that.

<div class="spoilers">

    @app.route("/tasks")
    def list_tasks():
        return render_template("list_tasks.html")
</div>

You'll have to create a "list\_tasks.html" file in the templates directory. Make it similar to the index.html file, but change the h1 tag to simply say 'Task List'.

Remember, a view is just a regular function. There is nothing special about it being part of a web app except that the return value of the view is sent to a browser. This means we can call any of the functions we've already written in our model file.

Let's review the 'get\_tasks' function in our model.py file. Here's a reference implementation, compare it to your own:

<div class="spoilers">

    def get_tasks(db, user_id):
        c = db.cursor()
        if user_id:
            query = """SELECT * from Tasks WHERE user_id = ?"""
            c.execute(query, (user_id,))
        else:
            query = """SELECT * from Tasks"""
            c.execute(query)
        tasks = []
        rows = c.fetchall()
        for row in rows:
            task = dict(zip(["id", "title", "created_at", "completed_at", "user_id"], row))
            tasks.append(task)

        return tasks
</div>

We can call this method and our model.connect\_db method directly from our view. We can then take the resulting list, and send it as a parameter to our template.

    @app.route("/tasks")
    def list_tasks():
        db = model.connect_db()
        tasks_from_db = model.get_tasks(db, None)
        return render_template("list_tasks.html", tasks=tasks_from_db)

Chew on this view for a moment. When a user accesses the "/tasks" url, it:

1. Connects to the database
2. Gets a list of all the tasks
3. Sends that list to the list\_tasks template as a parameter named 'tasks'

If we attempt to compartmentalize our view of the system, we can assume that when we render our template, we are receiving in the variable 'tasks' a list of dictionaries that represent all of the tasks in our database. We can then ignore all the other facts about our tasklist variable: where it came from, the functions required to execute it, etc. We have a list of task dictionaries, and that's all that matters.

Chapter 6: In Which We Try Formatting Our Data
----------------------------------------------
In our list\_tasks template, we do nothing with the 'tasks' variable. We need to display it on the screen. If we do the double-brace trick from before, we get bad output:

    {{ tasks }}

    Renders this in the html:
    [{'completed_at': None, 'created_at': u'2012-10-23 18:25:53', 'user_id': 1, 'id': 1, 'title': u'Finish this app'},
     {'completed_at': None, 'created_at': u'2012-10-23 18:25:53', 'user_id': 1, 'id': 2, 'title': u'Make it pretty'}]

We need to display this more sensibly. What we have is a list, and fortunately, html has a few mechanisms for displaying lists. Let's use the UL tag, the unordered list for this. Our final html should look like this:

    <ul>
    <li>Task 1: Finish this App</li>
    <li>Task 2: Make it pretty</li>
    </ul>

How do we do this in html? The short answer is we can't. The longer answer is that our templating language, [Jinja2](http://jinja.pocoo.org/docs/templates/) has the ability to include python-like code inside of our html, including for loops. Check the Jinja documentation and try building the loop on your own before checking your answer:

<div class="spoilers">
    
    <html>
        <head><title>Tipsy</title></head>
        <body>
            <h1>Task List</h1>
            <ul>
            {% for task in tasks %}
            <li>Task {{ task['id'] }}: {{ task['title'] }}</li>
            {% endfor %}
            </ul>
        </body>
    </html>
</div>

The Jinja for-loop is very much like a regular python for-loop and behaves in much the same way. Here, it must be wrapped in the {% %} characters, and it must have a matching {% endfor %} (we no longer have a sensible way to keep track of indentation inside of html.

For the most part, the line inside the for loop is essentially like a print statement. We could even write it like this, if we wanted:

    {{ "<li>Task " + task['id'] + ": " + task['title'] + "</li>" }}

This is valid, and uses standard string concatenation in python, but the first technique is preferable.

Reload your page and use 'view source' in the browser to see what the generated html looks like. Compare it to our template.

Chapter 7: A Brief Style Interlude
----------------------------------
Before we move on, we should add style to our templates. Download Bootstrap and unpack it into your project. Specifically, you will need to take the 'bootstrap.css' file and put it in your static/css directory, and then take the two png files in the package and put them in your static/img directory. You can ignore all the other files for now.

When you put a file in the static directory, you can access it in your browser directly. For example, if you put bootstrap.css in static/css, you can go to the following url to use it:

    http://localhost:5000/static/css/bootstrap.css

Bootstrap.css defines a good set of default styles for us to base our visual style on, and so we want to include it in our template. You have to use a &lt;link&gt; tag inside our head tag that links to the css file. Look this up and try it on your own. Use the spoiler if you need additional help:

<div class="spoilers">

    <head>
        <title>Tipsy</title>
        <link rel="stylesheet" href="/static/css/bootstrap.css" type="text/css">
    </head>
</div>

Reload the page and bask in the majestic beauty of bootstrap.

Take some time to play around with your template and see how it interacts with bootstrap. Notice that your text butts up against your margins, which is, in a word, 'hideous'. Look at the Bootstrap [Getting Started Guide](http://twitter.github.com/bootstrap/getting-started.html) and [other tutorials](http://lmgtfy.com/?q=bootstrap+tutorial) for some hints on how to make your page look better.

Chapter 8: In Which We Discover Forms
-------------------------------------
The idea that urls are matched to function calls is really powerful. So far we have called functions and displayed the result of the function call. But to create new data in our system, we need to call functions and pass in input from our user. For example, in the new\_task function, we need to get the task\_title and user\_id before calling that function. We'll simplify things for now and say that all tasks will be created and attached to user\_id 1.

Still, we need to get a title from the user. The usual way we collect data is with something called a form. It's like a paper form, a collection of fields to fill out. Let's make a new view attached to the url "/new\_task". It should render a template named "new\_task.html".

<div class="spoilers">

    @app.route("/new_task")
    def list_tasks():
        return render_template("new_task.html")
</div>

We need to create our new\_task.html file in our templates directory. To preserve the visual style we developed, we can just copy list\_tasks.html to our new file and replace the body.

In our new file, we need to add a [form](http://www.w3schools.com/tags/tag_form.asp). A form is composed of fields, and each field has a label identifying it. The form should also have a submit button that the user can click when they're done entering data.

Create a form with a text field and a submit button. The text field should have the name 'task\_title'. You can safely ignore the 'action' for now, and set the 'method' to be 'POST'.

<div class="spoilers">

    <form method="POST">
        <input type="text" name="task_title"></input>
        <input type="submit">
    </form>
</div>

Reload your page and fill out the form and see what happens when you click the submit button.

When you submit this form, nothing happens. It just reloads the page. That's because we haven't told the form what to _do_ with the data it's collected. We can think of the workflow of forms in two steps:

1. Collect the data into a form
2. Post (send) the data somewhere

What we've built is the form where data can be collected. Now we have to send it somewhere for processing. We specify the location to send it to through the 'action' parameter of the form. We don't _have_ anywhere to send it to just yet, so let's build that.

Chapter 9: In Which We Process Data From a Form
-----------------------------------------------
If we continue the idea that 'views' are functions that can be called by hitting a URL, we can build a function that processes our form data and creates a new Task in our database. It might look something like this.

    def new_task(task_title):
        db = model.connect_db()
        # Assume that all tasks are attached to user 1.
        task_id = model.new_task(db, task_title, 1)

If we were to wire up our function to a url, it might look like this:

    @app.route("/save_task") 
    def new_task(task_title):
        db = model.connect_db()
        # Assume that all tasks are attached to user 1.
        task_id = model.new_task(db, task_title, 1)

But, before you go and write this function, we have to discuss this glaring omission of detail. In this function, we receive a parameter called 'task\_title', but we don't know how to get that parameter from the form we created in the previous chapter and into our function call.

It turns out, there's no mechanism to do exactly what we're describing here. Instead, we need to use something called the 'request object' in Flask to get at this data. Modify your 'from flask import' line to look like this:

    from flask import Flask, render_template, request, redirect

Let's add our view to our file, but modify it a little bit.

    @app.route("/save_task", methods=["POST"]) 
    def new_task():
        task_title = request.form['task_title']
        db = model.connect_db()
        # Assume that all tasks are attached to user 1.
        task_id = model.new_task(db, task_title, 1)
        return "Success!"

Of note: we've changed our @app.route line to include the extra parameter, 'methods=["POST"]' so far we've been treating all url access as the same, but this isn't strictly true. When you access a url, you can tell the url exactly _how_ you're accessing it. By default, you 'get' a url. This is what happens when you type in a url into your browser. On the other hand, when you fill out a form and submit it, it 'posts' to a url. The form is posted, or sent to this url. This line we've added simply says that this url will respond to POSTed forms, rather than plain url requests.

We've also added this line:

    task_title = request.form['task_title']

Basically, in flask, the entire contents of a form are placed into a dictionary on the 'request' object. The request object is special and more or less represents the state of the user's browser when the request was made. One of the things it includes are the contents of forms.

Now that we have a place to send the contents of the form, we have to tell the form where that place is. We can just use the url of our view as the action parameter in our form.

<div class="spoilers">

    <form method="POST" action="/save_task">
        <input type="text" name="task_title"></input>
        <input type="submit">
    </form>
</div>

Earlier, we had a text input field named task\_title in our form:

    <input type="text" name="task_title"></input>

Once the form is submitted, the contents of this input field can be accessed by using its name as a key into the request.form dictionary. Try changing the dictionary key and the input field name and see how that works.

One last thing, when we create a new task, we need to give some feedback to the user that they've successfully created a new entry in the app. While it's lovely that we announce our success, a more common pattern is to simply let the user see their new data in the context of the app. Here, we just send the browser back to the url for the big list of tasks (called a redirect).

    @app.route("/save_task", methods=["POST"]) 
    def new_task():
        task_title = request.form['task_title']
        db = model.connect_db()
        # Assume that all tasks are attached to user 1.
        task_id = model.new_task(db, task_title, 1)
        return redirect("/tasks")

Chapter 10: In Which We Explore on Our Own
------------------------------------------
If all went well, you have a very rudimentary tasklist app that you can work with as a framework. However, it's still missing a lot of features

* The ability to mark a task as done (forms)
* The ability to log in as a particular user (forms, sessions)
* The ability to edit a task title (forms)
* The ability to split completed tasks off from incomplete tasks (Jinja templates)
* etc...

Compare this list with your earlier use case list and identify the next features you'd like to complete. You've seen almost all the components you need to do these things, with the exception of sessions. Try to piece that knowledge together to fill out the rest of your app.

Epilogue
--------
This is very rudimentary and we're intentionally doing things in a naive way to prevent information overload while exposing all the underpinnings of modern web development. In a later exercise, we'll take what we've built here and rebuild it in a more idiomatic fashion.
