"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from sqlalchemy import asc

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

    return render_template("user_list.html", users=users)


@app.route('/movies')
def movie_list():
    """ Show movies list. """

    movies = Movie.query.order_by(asc(Movie.title)).all()

    return render_template("movie_list.html", movies=movies)


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
    check_email = User.query.filter_by(email=user_email).first()
    
    # Check if user exists by email account.
    # if user exists...# pass
    if check_email:
        flash('User email already exists!')
        return redirect('/register')
    # if it doesn't exist
        # add user to database
    else:
        new_user = User(email=user_email, password=user_password)
        db.session.add(new_user)
        db.session.commit()  
         
    return redirect('/')


@app.route('/login', methods=["GET"])
def login():
    """ Get user email and password."""
    if session.get('user'):
        flash('Already logged in.')
        return redirect('/')
    else:
        return render_template('login.html')


@app.route('/login', methods=["POST"])
def login_process():    
    """ Verifies user credentials."""

    user_email = request.form.get('email')
    user_password = request.form.get('password')

    # Query for email address in db
    check_user = User.query.filter_by(email=user_email).first()

    if check_user:
    # Email matches corresponding password
        if check_user.password == user_password:
            # Add user_id to flask session
            session['user'] = check_user.user_id
            # redirect to '/' and flash 'logged in'
            flash('Logged in!')
            return redirect("/users/{}".format(check_user.user_id))
        else:
            flash('Invalid credentials.')
            return redirect('/login')
    else:
        flash('User not in system.')
        return redirect('/register')


@app.route('/logout')
def logout():
    """ Removes user from session. """
    if session.get('user'):
        del session['user']
        flash('Logged out')

    else:
        flash('Not logged in.')    

    return redirect('/')    


@app.route('/users/<int:user_id>')
def show_user_info(user_id):
    """ Search and provide user details """

    # Can simplify by passing entire user object to Jina and unpacking from there.
    user = User.query.options(db.joinedload("ratings")).filter_by(user_id=user_id).first()
    age = user.age
    zipcode = user.zipcode
    # See SQLAlchemy II lecture for using joined loads for ratings.
    ratings = user.ratings
    user_results = []
    
    # iterate through each ratings record
    for rating in ratings:
        title = rating.movie.title
        score = rating.score
        # create tuple containing Movie title and score
        user_results.append((title, score))
        # append to user_results
    return render_template('user-info.html', age=age, zipcode=zipcode, results=user_results)



@app.route("/movies/<int:movie_id>", methods=["GET"])
def show_movie_info(movie_id):
    """Provide movie details and allow user to rate."""

    movie = Movie.query.get(movie_id)

    return render_template('movie-info.html', movie=movie)


@app.route("/movies/<int:movie_id>", methods=["POST"])
def update_rating(movie_id):
    """Update ratings."""

    rating = request.form.get('rating')

    check_rating = Rating.query.filter_by(user_id=session['user']).first()
    if check_rating:
        check_rating.score = rating
    else:
        new_rating = Rating(movie_id=movie_id, user_id=session['user'], score=rating)
        db.session.add(new_rating)
        db.session.commit()

    flash('Thanks for rating! Please rate more!')
    return redirect('/movies')



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
