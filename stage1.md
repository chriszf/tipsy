Tipsy: Being a Tutorial on the Ways of Flask, Part the Second
=============================================================
If you haven't done it, do the [first part](index.html) of the Tipsy tutorial to get up to speed.

Chapter 0: In Which We Recenter Our Universe
--------------------------------------------
Because of all the possible things that could have been done for the first half of the tutorial, we're going to start this stage of the project from a new baseline. The [new repository](https://github.com/chriszf/tipsy/tree/stage1) has a complete workflow. You can:

1. View all the tasks
2. Create a task
3. Mark a task as complete

This time, I encourage you to fork and clone this branch directly.

Take some time to review the changes in the app. You'll find most of the changes in model.py. The file tipsy.py will have the remainder of the code changes. You will also find some new template files.

### Template Changes
Start the app by running

    $ python ./tipsy.py

And then visiting [http://localhost:5000/tasks](http://localhost:5000/tasks). The first thing you'll notice is that the new task creation form has been rolled into the same page as the list of all the tasks in the system. Spend some time reviewing how this was done in the 'list\_tasks' view and the file 'list\_tasks.html'. You'll also notice that you can click on a task's id, which brings you to a detail page where you can complete the task. This was implemented in the _view\_task_ and _complete\_task_ views.

In the list\_tasks template, we use a couple of Jinja constructs:

    {% for task in tasks %}
    <li>
        <a href="/task/{{task['id']}}">Task {{ task['id'] }}</a>:
            {{ task['title'] }}
            {% if task['completed_at'] %} &mdash; Completed
            {% endif %}
    </li>
    {% endfor %}

The URL we use in the &lt;a&gt; tag is partially constructed by pulling a value from the 'task' dictionary. Remember from the first exercise that Jinja is essentially a subset of python, and one feature that is directly usable in Jinja is dictionary access. On the next line, you can see that we use Jinja's if-statement to check whether or not a task has been completed (if its 'completed\_at\' attribute has been set), and display a message accordingly.

### Model Changes
The most significant change to the model is the addition of the make\_user and make\_task functions, both of which receive a row from our sqlite cursor. It takes the row and rolls it up into a dictionary, using the column names to access the fields. It uses the zip trick from the previous exercise:

    def make_user(row):
        fields = ["id", "email", "password", "username"]
        return dict(zip(fields, row))

The [zip function](http://docs.python.org/library/functions.html#zip) in conjunction with the [dict function](http://docs.python.org/library/functions.html#func-dict) (although dict is secretly just a class) is handy enough that I would recommend committing this one to memory.

### View Changes
The views are mostly as before, with the exception of the _view\_task_ and _complete\_task_ views, reproduced here:

    @app.route("/task/<int:id>", methods=["GET"])
    def view_task(id):
        db = model.connect_db()
        task_from_db = model.get_task(db, id)
        return render_template("view_task.html", task=task_from_db)

First, let's look at the @app.route lines for each. For _view\_task_, it routes to the url "/task/&lt;int:id&gt;". The latter half of the url indicates that this route will be matched by any url that starts with /task/ and ends with a number:

    /task/1
    /task/3000
    /task/32

The number in the dynamic portion of the url is then assigned to the parameter with a matching name in the view definition. Here, the &lt;int:id&gt; portion of the url is passed in as the sole parameter when calling _complete\_task(id)_.

Let's look at _complete\_task_, which, curiously, has the exact same url as _view\_task_.

    @app.route("/task/<int:id>", methods=["POST"])
    def complete_task(id):
        db = model.connect_db()
        model.complete_task(db, id)
        return redirect("/tasks")

The view itself is simple, calling complete\_task on the task id that it's invoked with, but how does the router (the mechanism that chooses which view) know to use one or the other? The differentiator here is the _methods_ parameter to the route. Although there are more methods for accessing urls, browsers typically access a url in one of two ways. The first, the GET, is used when you type a url into your browser, or click on a link. The concept is that you are accessing a url to _get_ the data contained therein.

The other mechanism is the POST. This cannot be invoked directly by a user. The only way to access a url via a POST is to submit a form. The _action_ for that form is the url that the data is posted to. The difference between the two is largely one of intent: with a POST request, you are submitting data somewhere to either be entered into a system as a new record or updating an existing record.

Chapter 1: In Which We Engage in Some Light Housekeeping
--------------------------------------------------------
With our new codebase, we have a reasonably decent task list system, but there's quite a bit of repetition, especially in our models and our templates. On top of that, there are some things which are 'brittle': all of our URLs are hardcoded in our templates. This early into the development of an app, it's hard to decide exactly what all the urls should look like, and it would be nice if we changed the url of a view, we didn't have to update all of our templates.

    <li>
        <a href="/task/{{task['id']}}">Task {{ task['id'] }}</a>:
            {{ task['title'] }}
            {% if task['completed_at'] %} &mdash; Completed
            {% endif %}
    </li>

Look at the _href_ in our &lt;a&gt; tag here. It is dynamically generated, but it is still hardcoded to start with the prefix "/task/". If we think about it, really we don't care what url is attached to the link. In terms of logical flow of our application, we're more interested in activating a specific view, rather than 'going to a url'. Let's look at the signature for the view in question:

    @app.route("/task/<int:id>", methods=["GET"])
    def view_task(id):

Remember, these lines say that the view _view\_task_ is attached to the url "/task/<int:id>". For this to work, somewhere deep in Flask it has to remember that the two are related. Somewhere, this mapping exists:

    view_task <=> /task/<int:id>

Internally, it probably is done this way:

    {"view_task": "/task/<int:id"}

Knowing that, it would be nice, if we had a view name, we could find out exactly what url it's attached to. Flask provides this facility to us in the form of the method __url\_for__. Given the _list\_tasks_ view, here is the behavior of __url\_for__.

    >>> url_for("list_tasks")
    "/tasks"

That's all fine and well, but our _view\_task_ view requires a parameter, namely, the id of a task to view. We can use [named parameters](http://www.diveintopython.net/power_of_introspection/optional_arguments.html) to populate it:

    >>> url_for("view_task", id=1)
    "/task/1"
    >>> url_for("view_task", id=5)
    "/task/5"

We can invoke this function in our template by wrapping it in double braces and treating it like a regular python function call. Try replacing the hard-coded urls in your views with dynamic ones generated by url for.

<div class="spoilers">

    <li>
        <a href="{{ url_for("view_task", id=task['id']) }}">Task {{ task['id'] }}</a>:
            {{ task['title'] }}
            {% if task['completed_at'] %} &mdash; Completed
            {% endif %}
    </li>
</div>
    
Do this for all of the urls in your views.

Chapter 2: In Which We Become Lazy
----------------------------------
Our code works, but there's a lot of repetition, both in our views and in our templates. As we've said before, the best programmers are the laziest programmers, so we should be attempting to find a way to avoid this repetition.

### The Templates
Our templates have a lot of boilerplate. We have a common layout for all of our pages, so we end up re-typing the html over and over for every page. There are two downsides. First, it's tedious to type and retype and retype, especially since we know it will be exactly the same every time. If we look at our views, the first 8 lines and the last 3 lines are the same in all of our files. The second downside shows up if we need to change our templates at all. For example, if we add a navigation bar in one file, we have to make sure that navigation bar is in every file.

Jinja2 offers an 'inheritance' mechanism to combat exactly this. We can define a _master_ template which contains the common layout for all of the pages. Extracting out the common parts of all our pages, we get this:
    
    <!DOCTYPE html>
    <!-- layout.html -->
    <html>
        <head>
            <title>Tipsy Task List</title>
            <link rel="stylesheet" href="/static/css/bootstrap.css" type="text/css">
        </head>
        <body>
            <div class="container">
            {% block body %}{% endblock %}
            </div>
        </body>
    </html>

Save the contents into a file called layout.html in your templates folder. This is essentially a regular html file, but with a {% block %} statement in the middle. This is Jinja's way of saying that this section (which is empty at the moment) will potentially be replaced later. Expanding our mad lib analogy, essentially we're declaring a blank spot that we can later fill. It's like variable substitution with our {{ }} operator, but our variable here instead is a large chunk of html.

To use this, open up our list\_tasks.html file and replace it entirely with the following lines:

    {% extends "layout.html" %}
    {% block body %}
    <h1>Task List</h1>
    <div class="tasklist">
        <ul>
        {% for task in tasks %}
        <li><a href="/task/{{task['id']}}">Task {{ task['id'] }}</a>: {{ task['title'] }}{% if task['completed_at'] %} &mdash; Completed{% endif %}</li>
        {% endfor %}
        </ul>
    </div>

    <form method="POST" action="/save_task">
        <label for="title">New Task Item
        <input type="text" name="title" id="title"></input>
        <input type="submit"></input>
    </form>
    {% endblock %}

What we've done here is removed all of the common html tags (the ones that we put into layout.html) and replaced it with two statements, a {% extends %} statement and a {% block %} statement. What this does is it first loads the file that we're extending, in this case, layout.html. Then, it finds all of the block statements in that file, and replaces them with the contents of the matching blocks in our list\_tasks.html file.

Browse to [http://localhost:5000/tasks]:(http://localhost:5000/tasks) in your browser. It should look exactly the same as before. Try adding html to the list\_tasks file and the layout file and see how the two interact. Update all of your templates to extend from the same layout.

### The Views
There's a lot of repetition in our view code, but most of it is necessary for things to work. Still, we'll try to remove what we can. One thing that shows up repeatedly is the following line:

    db = model.connect_db()

It shows up in every single view that we have, so it would be nice not to retype it every time. Flask has a mechanism called the __before\_request__. It's a function that we can specify to be called right before every view is executed. We can write the function as such:

    @app.before_request
    def set_up_db():
        db = model.connect_db()

Now, **set\_up\_db** will be called before every view when a web browser accesses it. We can now remove that line from our views:

    @app.route("/task/<int:id>", methods=["GET"])
    def view_task(id):
        task_from_db = model.get_task(db, id)
        return render_template("view_task.html", task=task_from_db)

You may be asking, how does the 'db' variable get from **set\_up\_db** to **view\_task**? (If you didn't ask, you should be now.) The answer is it doesn't. At this point, you might be thinking that a global variable is a good idea, since there's no obvious way to connect the two functions together, without resorting to our duplicated code from before. For the record, this is the only time ever that global variables are a good idea.

Except that we can't use them. Our app, if we step back for a second, is really a web server. This means it is designed to service many different clients simultaneously. If we use a global variable, one user may come in and connect to the database and create a cursor in the middle of another user also creating a cursor, potentially _clobbering_ the other's cursor.

Instead, we have to use a special global variable that Flask gives us. Update your import line as follows:

    from flask import Flask, render_template, redirect, request, session, g

We've added _session_ (which we'll use later) and _g_, which we'll use now. The _g_ variable is a special global variable provided by flask that gets around the multi-user clobbering problem described earlier. We can use it as if it were a module, reading from and assigning to it as we like. Change our **set\_up\_db** function:

    @app.before_request
    def set_up_db():
        g.db = model.connect_db()

And we can update the matching line in our view to use our special global:

    task_from_db = model.get_task(g.db, id)

While we're here, we can add a __teardown\_request__ function that cleans up after each view. Even though it isn't strictly necessary in this case, we can close our connection to our database when we're done using it. The method on the _db_ object is __close__.

<div class="spoilers">

    @app.teardown_request
    def disconnect_db():
        g.db.close()
</div>

Simplify the rest of the views and make sure everything still works.

Chapter 3: In Which We Cure Our App of Amnesia
----------------------------------------------
Web servers are 'stateless'. Our app just blindly executes the view that we request. We can also jump from view to view with impunity: at no point does it remember, nor does it care, what the previous view you looked at was. Or if you even looked at a view. Essentially, our application has no memory of previous actions.

Interestingly, it _seems_ to have memory because we can add tasks to the system and it remembers when we do. If we think about it for a second, you'll realize that it's the database that has memory. The app just blindly asks the database for data, and displays whatever the _database_ remembers.

We can build all manner of apps, even if our app never learns our name. The only problem is, if it never remembers our name, it could never differentiate between different people using it. Obviously, we need to rectify this.

There is a dictionary called 'the session'. The session is a piece of data shared between a web server and a browser. Note, this session is shared for all browser windows as well (excepting incognito windows). Each browser has its own session; no two browsers share the same session.

From the server side, the session is a dictionary named _session_. We can put things in the session as if it were a regular dictionary:

    @app.route("/set_date")
    def set_date():
        session['date'] = datetime.datetime.now()
        return "Date set"

Similarly, we can get data out of the session just like a regular dictionary, even in a different view:

    @app.route("/get_date")
    def get_date():
        return str(session['date'])

The session is shared between views. Notice that we don't need to specify _whose_ session we're looking at. There is some flask voodoo that automatically sets the value of the _session_ variable to be the correct dictionary for the appropriate browser. To reiterate: the session variable is always set to the session of the current browser.

The strategy to use this then, is to put some uniquely identifying information into a browser session, and to use that to limit the resources we display to the user. One piece of unique information we have is the user id. If we can store this in a browser's session, we can tell which user is using that browser.

Therefore, being logged in can be thought of as the browser carrying around an id card that identifies it to the server.Let's start by giving a user a place to log in. Make a new view named _login_ that renders a template named _login.html_. Make the view respond to the "/login" url. The template should inherit from our base layout and provide a form where a user can enter their email address and password. We can omit the form action for now.

<div class="spoilers">

    {% extends "layout.html" %}
    {% block body %}
    <form>
    <input type="string" name="email">
    <input type="password" name="password">
    <input type="submit">
    </form>
    {% endblock %}
</div>

Now, we need to make a view to receive the login credentials. Name it _authenticate_, and it should be attached to the url "/authenticate". It should respond to a POST method, and receive the user's email and password from a form, then call our **authenticate** function in our model module. This function returns the _id_ of any user who correctly authenticates. We should store this id in the session.

<div class="spoilers">

    @app.route("/authenticate", methods=["POST"])
    def authenticate():
        email = request.form['email']
        password = request.form['password']
        user_id = model.authenticate(g.db, email, password)
        session['user_id'] = user_id
</div>

After we've successfully authenticated, we can modify any user-sensitive views to check for the presence of a user id in the session before proceeding. Modify the _list\_tasks_ view to check for a user id before querying the database.

<div class="spoilers">

    @app.route("/tasks")
    def list_tasks():
        db = model.connect_db()
        user_id = session.get("user_id", None)
        tasks_from_db = model.get_tasks(db, user_id)
        return render_template("list_tasks.html", tasks=tasks_from_db)

</div>

Epilogue: In Which We Are Satisfied With Our Work
-------------------------------------------------
Our app is pretty complete at this point in terms of functionality. Now is a good time to import any features from the first version of your app into the newer version, with the new constraints.

There are still improvements we can make, mostly related to the model, and _many_ improvements we can make with regards to error checking (hint: we didn't do any), but we now have the tools to build a flask webapp idiomatically.
