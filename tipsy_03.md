Tipsy: Being a Tutorial on the Ways of Flask, Act Three
=======================================================
Complete the [first](index.html) and [second](stage1.html) parts before doing this section.

Chapter 0: In Which We Wonder Why We're Still Here
--------------------------------------------------
At this point, we have most of the idiomatic methods for building an application with Flask securely under our belts, with but few things remaining:

1. The ['message flash'](http://flask.pocoo.org/docs/patterns/flashing/)
2. Simple [form validation](http://flask.pocoo.org/docs/patterns/wtforms/)

Neither of these things is especially difficult (nor are they necessary at this point), and can be learned in the comfort of your own home, next to a fire, sipping hot cocoa or a beverage of your own choosing. No, friends. Today, we're here to address the looming monstrosity that is our model.py file.

As we mentioned before, the best programmers are lazy and will avoid repetition at all costs. Alas, our model.py file is riddled with repetition. The good news is that it's repetition of a sort that can be dissolved away through the arcane incantations of object-oriented programming. Only, the path to success here is fraught with perils and terrors of a sort beyond the imaginings of man. Tread ye lightly, for here monsters dwell.

    Note: There are no monsters in our model.py file.

Actually, it turns out our model.py file isn't quite that bad, but the solutions to clean it up are all a bit on the tricky side. We'll rewrite it two ways, the first being a functional approach, and the second being object-oriented. The latter is the preferred mechanism. Afterwards, we'll introduce the mystical 'ORM' that we've talked about so much, and see how it fits in to solve all of our problems.

Chapter 1: In Which We Perform Acrobatics With Functions
--------------------------------------------------------
Reptition is the bane of the lazy, and we should all strive to be as lazy as possible. If you ever find yourself doing something twice and think, "ugh, this would be annoying to do a third time," you might consider refactoring your code. Consider the following excerpt from our model file:

    def get_user(db, user_id):                                 
        c = db.cursor()
        query = """SELECT * from Users WHERE id = ?"""
        c.execute(query, (user_id,))
        user_row = c.fetchone()
        if user_row:
            return make_user(user_row)
        return None

    def get_task(db, task_id):
        c = db.cursor()
        query = """SELECT * from Tasks WHERE id = ?"""
        c.execute(query, (task_id,))
        task_row = c.fetchone()
        if task_row:
            return make_task(task_row)
        return None

I assure you, if you put these two function definitions side-by-side, you would find that they look nearly identical, a near copy-paste. Paste them into your editor and try for yourself, just to be really sure. These two functions are the perfect candidate for _abstraction_. In the process of abstraction, we extract the common aspects of these two functions and move them into a separate function. This simplifies our original functions further, and gives us a basis for extending our program without resorting to copying and pasting again.

    def common_bits(id):
        # Do something super clever
        pass

    def get_user(db, user_id):                                 
        return common_bits(db, user_id)

    def get_task(db, task_id):
        return common_bits(db, task_id)

    # And theoretically, if we get to the point of 
    # adding comments to our app,
    def get_comment(db, comment_id):
        return common_bits(db, comment_id)

To accomplish this, we first need to identify the common bits. Let's scrutinize our functions again.

You'll notice that really, the only two differences are that our query is slightly different, and we call the function **make\_task** in one and **make\_user** in the other.

### The Query
If we really look at the queries, they're really not all that different at all:

    user_query = """SELECT * from Users WHERE id = ?"""
    task_query = """SELECT * from Tasks WHERE id = ?"""

Both of these could be generated from a standard string template:

    query_template = """SELECT * from %s WHERE id = ?"""
    user_query = query_template%("Users")
    task_query = query_template%("Tasks")

    # and because we can
    comment_query = query_template%("Comments")

Knowing this, we can produce the following abstract version of our original functions that works on any table. It will be called **get\_from\_table\_by\_id** and will accept a db connection, the table name, and the id we're querying for. It will return a dictionary with the keys being the column name of that table, and the values being pulled from the appropriate record. Try implementing this function now. Scroll ahead past the spoiler to see how it will end up being used, if you need a hint.

<div class="spoilers">

    def get_from_table_by_id(db, table_name, id):
        c = db.cursor()
        query_template = """SELECT * from %s WHERE id = ?"""
        query = query_template%table_name
        c.execute(query, (id,))
        row = c.fetchone()
        if row:
            if table_name == "Users":
                return make_user(row)
            elif table_name == "Tasks":
                return make_task(row)
        return None
</div>

With that in place, our **get\_user** and **get\_task** functions simply become:

    def get_user(db, user_id):
        return get_from_table_by_id(db, "Users", user_id)

    def get_task(db, task_id):
        return get_from_table_by_id(db, "Tasks", task_id)

### The Functions
Things are looking pretty good, but take a look at our reference implementation in the spoiler. We use an 'if' statement to decide whether to call **make\_user** or **make\_task**. We've reduced a lot of our code, but we still have to modify this if statement every time we add a new table. The problem is, it doesn't look like there's any other way to choose the correct function to call.

This perspective is only true if you're looking at the problem in terms of typical _procedural programming_, which is what we've been doing. There's very much a "do this then do that" mindset to procedural programs, and a strong mental separation between variables (data) and code: data is data, and code _performs actions_, so therefore they're two different things.

Contrast this with one the tenets of *functional programming*, which is that data and code are the same thing. The only difference is, code is data that can be executed. Let's see how this plays out in the python shell. First, let's assume that a function is where you put code, and a variable is where you put data. Next, fire up a shell and repeat the following exercise:

    >>> a = 5           # 'a' is our variable
    >>> def my_fn():    # 'my_fn' is our function
    ...     print "Hello"
    ... 
    ... 
    >>> print a         # we expect it to return 5
    5
    >>> print my_fn     # notice the lack of parens

Before we go on, guess what the last line prints.

<div class="spoilers">

    >>> print my_fn     # notice the lack of parens
    <function my_fn at 0x10ec799b0>
</div>

You may not have expected that. What python is showing us is that **my_fn**, in addition to being a function, is also a variable. The *my_fn* variable contains the code to be executed, but that code is **not** run unless we add parentheses:

    >>> my_fn()
    Hello
    >>> my_fn
    <function my_fn at 0x10ec799b0>

This lets us do a certain amount of gymnastics with our function:

    >>> b = my_fn
    >>> b()
    Hello
    >>> d = { "key": my_fn }
    >>> d['key']()
    Hello
    >>> l = [my_fn, my_fn]
    >>> l[-1]()
    Hello

Here, we've put assigned the code in **my_fn** to another variable, placed it in a dictionary, and placed it in a list. None of these things have inhibited our ability to invoke that code, which we can do at any time by adding parentheses.

With this trick, we can modify our **get_user** and **get_task** functions above to simply pass along the appropriate function to call of **make_user** and **make_task** when needed:

    def get_user(db, user_id):
        return get_from_table_by_id(db, "Users", user_id, make_user)

    def get_task(db, task_id):
        return get_from_table_by_id(db, "Tasks", task_id, make_task)

Modify **get_from_table_by_id** to accept the function used to make the appropriate dictionary as the final parameter.

<div class="spoilers">

    def get_from_table_by_id(db, table_name, id, make_dict_fn):
        c = db.cursor()
        query_template = """SELECT * from %s WHERE id = ?"""
        query = query_template%table_name
        c.execute(query, (id,))
        row = c.fetchone()
        if row:
            return make_dict_fn(row)
        return None
</div>

Chapter 2: In Which We Go For the Gold on the Functional Pommel Horse
---------------------------------------------------------------------
We'll try to do something similar with the **new_user** and **new_task** functions. The difference here is that you've got a variable number of columns, which will be different for each table. You also have to contend with the fact that we use a DATETIME('now') statement in one of our queries. You'll need a few tricks to solve this one. Adding the following lines at the top of your file may give you some ideas.

    TASK_COLS = ["id", "title", "created_at", "completed_at", "user_id"]
    USER_COLS = ["id", "email", "password", "username"]

It's also vague enough that it might not give you any ideas. Some more hints:

1. You'll need to use the following construct: ", ".join(some\_list)
2. Hint 1 is the only hint.

Basically, we need a way to dynamically create a query string with the correct number of question marks in it. We'll make this easier on ourselves by taking the DATETIME out of our task query, as well as the second null. We can fill them back in later.

    user_query = """INSERT INTO Users VALUES (NULL, ?, ?, ?)"""
    task_query = """INSERT INTO Tasks VALUES (NULL, ?, ?, ?, ?)"""

We can start by extracting our query template, the common parts of each query:

    query_template = """INSERT INTO %s VALUES (%s)"""

We know how to fill in the first %s, it is simply the table name. The question mark part is a little tricky, but we have all the information. Remember, an insert statement requires a value for every column in the table...

<div class="spoilers">
... and we've created two variables above that are lists of every column title in our table.
</div>

_Just in case you wanted to have an a-ha moment, we've hidden the remainder of that thought. Go ahead and uncover this spoiler, it's not that important. Now back to the regularly scheduled tutorial._

If our table has N columns, we need to create a string that has a "NULL", followed by N question marks, each separated by a comma. Construct this any way you like, for loops, list comprehensions, hamsters. My favorite way uses list addition and multiplication:

<div class="spoilers">

    >>> USER_COLS = ["id", "email", "password", "username"]
    >>> num_cols = len(USER_COLS)
    >>> strings = ["NULL"] + ["?"] * (num_cols-1)
    >>> print strings
    ['NULL', '?', '?', '?']
    >>> final_str = ", ".join(strings)
    >>> print "%r"%final_str
    'NULL, ?, ?, ?'
</div>

Now we can take this and try to build our abstract insert function.

<div class="spoilers">

    def insert_into_table(db, table, columns, values):
        c = db.cursor()
        query_template = """INSERT into %s values (%s)"""
        num_cols = len(columns)
        q_marks = ", ".join(["NULL"] + (["?"] * (num_cols-1)))
        query = query_template%(table, q_marks)
        res = c.execute(query, tuple(values))
        if res:
            db.commit()
            return res.lastrowid
</div>

The simplification of **new_user** is fairly straightforward:

    def new_user(db, email, password, name):
        vals = [email, password, name]
        return insert_into_db(db, "Users", USER_COLS, vals)

The simplification of **new_task**, on the other hand, requires a little more thought. We need to reintroduce the DATETIME statement we removed earlier in the abstraction process. We also need to throw in a null. Fortunately, we can replace sqlite's DATETIME mechanism with Python's datetime mechanism, which is ultimately more portable anyway. (The sqlite datetime statement does not work in either postgres or mysql.) As for the null, it turns out we can replace that with python's None type.

<div class="spoilers">

    # Add this to the very top of your file
    import datetime

    def new_task(db, title, user_id):
        vals = [title, datetime.datetime.now(), None, user_id] 
        return insert_into_db(db, "Tasks", TASK_COLS, vals)
</div>

Chapter 4: In Which the Old Ones Resurface
------------------------------------------
It's been some time now since we've talked about objects, so let's talk about objects.

Everything we've done so far was to expose you to the delights (horrors) of working with a wonderful (migraine-inducing) database (database). In doing so, we've done a couple of things which aren't bad per se, but can be considered 'code smells', and would have been better accomplished using objects.

Take our 'user' dictionary that represents my row:

    {"id": 1, "email": "c@hackbright.com", "password": "securepassword", "name": "Christian"}

We can extrapolate this to say that the archetypal dictionary for user records contains the following keys

    id
    email
    password
    name

And that every row that we extract from our database should use this format. Additionally, we have a list of all the column names for this table.

    USER_COLS = ["id", "email", "password", "username"]

Furthermore, we have a number of functions related specifically to these user rows, either extracting them or inserting them.

    new_user
    get_user
    authenticate

If only there was a construct we could use that could use that could organize both code and data into a single place...

Oh.

So this is really an excellent place for objects, because we can pack everything together into one tidy bundle. Let's go about converting the user dictionary into a class. First, we start by specifying the **\_\_init\_\_** method.

    class User(object):
        def __init__(self, id, email, password, name):
            self.id = id
            self.email = email
            self.password = password
            self.name = name

If we stopped here, we could change our **make_user** function to look like this:

    def make_user(row):
        return User(row[0], row[1], row[2], row[3])

And already, this would be a pretty great boon. It would cut down on some awkward typing in our templates. For example:

    <h1>Welcome back {{ user['name'] }}!</h1>

    could become

    <h1>Welcome back {{ user.name }}!</h1>

Even though they're functionally identical, I prefer the syntax of the latter.

Still, this is thinking pretty small. We want to think big with objects. We want to embrace _encapsulation_. We want to put every single function related to User data onto our User class. Too bad it's not as simple as just putting our methods directly inside the class definition.

Oh wait, it is.

    class User(object):
        # init omitted for brevity

        # This is formerly the new_user function
        @classmethod
        def new(cls, db, email, password, name): 
            vals = [email, password, name]
            return insert_into_db(db, "Users", USER_COLS, vals)
           
There is a slight change here. First, we've changed the name. To call this method, we do the following:

    user_id = User.new(db, "c@hackbright.com", "securepassword", "Christian")

It seemed redundant to type in **User.new_user**. The second thing is the addition of the @classmethod decorator and the cls parameter.

Remember that a normal instance method is defined with 'self' as being the first parameter to the method, to give the method a mechanism for accessing the instance that it lives on. Here, we have a _class method_. It's a method that's _related_ to Users, but not to a _specific_ user. As an example, the following wouldn't make much sense:

    >>> me = User(1, "c@hackbright.com", "password", "Christian")
    >>> me.new("d@hackbright.com", "password", "David")

Here, we create a new instance that represents _me_, and then somehow delegate the task of creating a new record for David to that instance. No, the act of creating a new record in our database should fall squarely on the shoulders of the class User itself. Again, it's related to Users, but not to specific users.

A class method is not too dissimilar from an instance method. Instead of being attached to an instance, it's attached to a class. And in the same way that an instance method frequently needs a way to reference the instance it's attached to, the class method needs a reference to the class it's attached to, and that's the 'cls' parameter.

Why would we need that? Well, we have something called a _class attribute_, which is a variable that's available to all instances of a given class. Frequently, it's a constant:

    class Cat(object):
        NUM_LEGS = 4

With this, all Cat instances will have a .NUM\_LEGS attribute that will always equal 4. We can also do the following:

    >>> print Cat.NUM_LEGS
    4

There is one variable we have here that makes sense to turn into a class attribute. Review the opening paragraphs of the chapter to see if anything fits the description.

    CUE JEOPARDY THEME MUSIC

That's right, we have the USER\_COLS variable, which will be the same for every single user object. We can update our class definition to include the variable.

    class User(object):
        COLS = ["id", "email", "password", "username"]
        TABLE_NAME = "Users"
        # methods omitted for brevity
        
Again, accessing the list of columns by typing User.USER\_COLS seemed redundant, so we renamed it. While we were at it, we added the table name to the list of class attributes. This is another thing that's going to be common for all instances of the User class: the name of the database table it's attached to. Now that our class has all these class attributes, we can use them in our class method. Try to determine the syntax for this yourself.

<div class="spoilers">

    class User(object):
        COLS = ["id", "email", "password", "username"]
        TABLE_NAME = "Users"

        @classmethod
        def new(cls, db, email, password, name): 
            vals = [email, password, name]
            return insert_into_db(db, cls.TABLE_NAME, cls.COLS, vals)
</div>

One thing to note, class attributes are not limited to access by the class it lives on. We can always refer to the class attributes from _outside_ a class method by using the full class name:

    >>> print User.TABLE_NAME
    Users

Now, change the authenticate method from being a stand-alone function to a class method in the same way. It will be slightly tricky because you'll need to create an instance of the User class from _inside_ a method _on_ the User class.

<div class="spoilers">

    @classmethod
    def authenticate(cls, db, email, password):
        c = db.cursor()
        query = """SELECT * from %s WHERE email=? AND password=?"""%(cls.TABLE_NAME)
        c.execute(query, (email, password))
        result = c.fetchone()
        if result:
            return cls(*result)
            # the asterisk in the line above makes it equivalent
            # to the line below:
            # return cls(result[0], result[1], result[2], result[3])
        return None
</div>

For the next step, try to convert all of the task-related methods and variables into a single Task class. Since the **complete_task** function works on a _specific_ task, it's a good candidate for turning into an instance method, if you can figure out how to fit that into the workflow. You'll need to update all of your views to use the classes. You'll also need to update your templates to use these new classes. For the most part, that just means you can change lines like this:

    <li>{{ task['title'] }}</li>

    to

    <li>{{ task.title }}</li>

Chapter 5: In Which a Challenge Is Issued Without Guidance
----------------------------------------------------------
One thing which we glazed over are the relationships between the tables. That information is present in the .user\_id attributes in our tables, but it would be nice if we made the relationship more concrete.

Since tasks _belong_ to a user, it makes sense that rather than ask the Task class to return all the Tasks that match a user, we should be asking a User instance for all of the tasks that belong to it.

    >>> me = User.get(db, 1)
    >>> print me.get_tasks()
    ["Wash the dog", "Wash the cat", "Wash the fish?!"]

Rewrite your **get_tasks** function to be a part of the User class, rather than the Task class.

Epilogue: In Which We Wonder What All the Fuss Over ORMs Is About
-----------------------------------------------------------------
Writing tedious code builds character, and so far, we've written a fair amount of tedious <br>database &lt;&mdash;&gt; object code. If you don't see it, trust me that objects are far more convenient here than dictionaries, so it was worthwhile.

Still, it _was_ tedious, there is no doubt, and there's a lot of boilerplate. Every place we have a sql query, there was some way to automate part or all of it based on class attributes, like the table name, or the field list.

An ORM is a piece of software that does exactly exactly this automation. It allows you to declare a class like this:

    # This won't work without the right ORM module
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True)
        email = db.Column(db.String(120), unique=True)
        password = db.Column(db.String(120))

        def __init__(self, username, email, password):
            self.username = username
            self.email = email
            self.password = password

This particular ORM can look at our class definition and _construct a sql table from it_. This means no more making a schema.sql by hand. It also lets us do things like this:

    me = User.get(1)    # get user by id from the db
    me.email = "zebulon@hackbrightacademy.com"
    me.save()           # save to the database

In this bit of code, the ORM automatically generates the SQL to create a SELECT query to pull a record out of the database, then turn it into a class. After we change the attributes on the class to our liking, it lets us call a .save() method, which automatically creates the UPDATE statement that does the correct thing and commits it to the database. It's like magic!

The specific kind of magic here is alchemy (actually, [SQLAlchemy](http://www.sqlalchemy.org/)), which is appropriate, given how it transmutes database records into objects and backs. If you would like to learn more about it, and how to integrate it with flask, check out the [quickstart guide](http://packages.python.org/Flask-SQLAlchemy/quickstart.html).

The last step here is to replace our model file entirely with an ORM-enabled one and rejoice in the fact that except in rare cases, you don't have to mess with constructing SQL queries by hand anymore.

And that's it. You're now a web developer. We can all go home.

Or can we?

#### To be continued...
