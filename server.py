"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route('/users')
def user_list():
    """ Show list of users. """

    users = User.query.all()

    return render_template("users_list.html", users=users)


@app.route('/register', methods=["GET"])
def register_form():
    """ Collect email and password. """

    return render_template("registration.html")


@app.route('/register', methods=["POST"])
def register_process():
    """ Checks user input for new account. """

    # take user email
    user_email = request.form.get('email')
    user_password = request.form.get('password')


    # check to see if exists in database
    check_email = User.query.filter_by(email=user_email).all()
    print check_email
    # Check if user exists by email account.
    # if user exists...# pass
    if check_email:
        pass
    # if it doesn't exist
        # add user to database
    else:
        print "We're in the else statement!"
        new_user = User(email=user_email, password=user_password)
        print "New user" , new_user
        db.session.add(new_user)
        db.session.commit()  
         
    return redirect('/')



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
