"""
Movie Web Application

This Flask application allows users to manage their movie collections,
including adding, viewing, updating, and deleting movies.
It integrates with an SQLite database for persistence and the OMDB API for fetching movie details.
"""

import omdbapi
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from datamanager.sqlite_data_manager import SQLiteDataManager, User, Movie, UserMovieLibrary

# Define paths for database setup
MAIN_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = "./data"
DB_NAME = "moviwebapp.sqlite"
DB_PATH = os.path.join(MAIN_FOLDER_PATH, DB_PATH, DB_NAME)

# Initialize Flask app
app = Flask(__name__)
data_manager = SQLiteDataManager(DB_PATH)  # Use the appropriate path to your Database

# Secret key for session management and flash messages
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
data_manager.db.init_app(app)

# Create database if it doesn't exist
if not os.path.exists(DB_PATH):
    with app.app_context():
        data_manager.db.create_all()
        print("New DB Created")


@app.route('/')
def home():
    """
    Render the home page of the application.

    Returns:
        Rendered HTML template for the home page.
    """
    return render_template('home.html')


@app.route('/users')
def list_users():
    """
    Fetch and display all users.

    Returns:
        Rendered HTML template displaying a list of all users.
    """
    try:
        users = data_manager.get_all_users()
    except Exception as e:
        app.logger.error(f"Error fetching users: {e}")
        users = []
    return render_template('users.html', users=users)


@app.route("/users/<int:user_id>")
def user_profile(user_id):
    """
    Fetch and display the user's movie collection.

    Args:
        user_id (int): ID of the user.

    Returns:
        Rendered HTML template displaying the user's movies.
    """
    try:
        movies = data_manager.get_user_movies(user_id)
    except Exception as e:
        app.logger.error(f"Error fetching users: {e}")
        movies = []
    return render_template('user_movies.html', movies=movies, user_id=user_id)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Add a new user to the system.

    Methods:
        GET: Render the add user form.
        POST: Process the form and add the user.

    Returns:
        Redirect to user list on success or re-render form on failure.
    """
    if request.method == "POST":
        try:
            user_name = request.form.get('name')
            if not user_name or len(user_name.strip()) == 0:
                app.logger.error("Name cannot be empty", "error")
                return render_template("add_user.html")
            user = User(name=user_name.strip())
            data_manager.add_user(user)
            app.logger.info("User added successfully", "success")
        except Exception as e:
            app.logger.error(f"Error adding user: {e}")
        return redirect(url_for('list_users'))
    return render_template("add_user.html")


@app.route("/users/<int:user_id>/add_movie", methods=['GET', 'POST'])
def add_movie(user_id):
    """
    Add a new movie to a user's collection.

    Args:
        user_id (int): ID of the user.

    Methods:
        GET: Render the add movie form.
        POST: Process the form and add the movie to the database.

    Returns:
        Redirect to the user's movie list on success or re-render form on failure.
    """
    if request.method == "POST":
        movie_title = request.form.get('title')
        try:
            omdb_movie = omdbapi.get_movie_info(movie_title)
            if not omdb_movie:
                app.logger.error("No movie found or an error occurred", "error")
                return render_template('add_movie.html', user_id=user_id, movies=data_manager.get_user_movies(user_id))

            movie = Movie(
                title=omdb_movie['title'],
                year=omdb_movie['year'],
                rating=omdb_movie['rating'],
                poster=omdb_movie['poster'],
                director=omdb_movie['director'],
            )

            if data_manager.add_movie(movie):
                relationship = UserMovieLibrary(user_id=user_id, movie_id=movie.id)
                data_manager.add_user_movie_relationship(relationship)

        except Exception as e:
            app.logger.error(f"Error adding movie for user {user_id}: {e}")
        return render_template('notification.html', msg='Movie successfully added', user_id=user_id)

    return render_template("add_movie.html", movies=data_manager.get_user_movies(user_id), user_id=user_id)


@app.route("/users/<int:user_id>/movie/<int:movie_id>", methods=['GET'])
def show_movie(user_id, movie_id):
    """
    Display detailed information about a specific movie in a user's collection.

    Args:
        user_id (int): ID of the user.
        movie_id (int): ID of the movie.

    Returns:
        Rendered HTML template displaying movie details.
    """
    movie = data_manager.get_movie_by_id(movie_id)
    if not movie:
        app.logger.info("Movie not found", "error")
        return redirect(f"/users/{user_id}")

    relationship = data_manager.get_user_movie_relationship(user_id, movie_id)
    if not relationship:
        app.logger.info("Relationship not found", "error")
        return redirect(f"/users/{user_id}")

    return render_template('movie.html', movie=movie, relationship=relationship)


@app.route("/users/<int:user_id>/update_movie/<int:movie_id>", methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """
    Update details of a movie in a user's collection.

    Args:
        user_id (int): ID of the user.
        movie_id (int): ID of the movie.

    Methods:
        GET: Render the update movie form.
        POST: Process the form and update the movie details.

    Returns:
        Rendered notification on success or redirect to the user's movies.
    """
    relationship = data_manager.get_user_movie_relationship(user_id, movie_id)
    movie = data_manager.get_movie_by_id(movie_id)

    if not movie:
        flash("Movie not found", "error")
        return redirect(f"/users/{user_id}")

    if not relationship:
        flash("Relationship not found", "error")
        return redirect(f"/users/{user_id}")

    if request.method == "GET":
        return render_template('update_movie.html', relationship=relationship, movie=movie)

    # Update movie details
    movie.title = request.form.get('title')
    movie.director = request.form.get('director')
    movie.year = request.form.get('year')
    movie.rating = request.form.get('rating')
    data_manager.update_movie(movie)

    # Update relationship details
    relationship.notes = request.form.get('notes')
    data_manager.update_relationship(relationship)

    flash("Movie successfully updated", "success")
    app.logger.info(f"User {user_id} updated movie {movie_id}")
    return render_template('notification.html', msg='Movie successfully updated', user_id=user_id)


@app.route("/users/<int:user_id>/delete_movie/<int:movie_id>", methods=['GET'])
def delete_movie(user_id, movie_id):
    """
    Remove a movie from a user's collection.

    Args:
        user_id (int): ID of the user.
        movie_id (int): ID of the movie.

    Returns:
        Rendered notification on success or redirect to the user's movies.
    """
    relationship = data_manager.get_user_movie_relationship(user_id, movie_id)
    if not relationship:
        flash("Movie not found in user's library", "error")
        return redirect(f"/users/{user_id}")

    data_manager.remove_movie_from_user(user_id, movie_id)

    flash("Movie successfully deleted", "success")
    app.logger.info(f"Movie {movie_id} removed from user {user_id}'s library")
    return render_template('notification.html', msg='Movie successfully deleted', user_id=user_id)


# Handle 404 Not Found
@app.errorhandler(404)
def page_not_found(e):
    """
    Handle 404 errors (Page Not Found).

    Args:
        e (Exception): The exception object.

    Returns:
        Rendered HTML template for 404 error and status code 404.
    """
    app.logger.error(f"404 Error: {e}")
    return render_template('404.html'), 404


# Handle 500 Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
    """
    Handle 500 errors (Internal Server Error).

    Args:
        e (Exception): The exception object.

    Returns:
        Rendered HTML template for 500 error and status code 500.
    """
    app.logger.error(f"500 Error: {e}")
    return render_template('500.html'), 500


# Handle 403 Forbidden
@app.errorhandler(403)
def forbidden(e):
    """
    Handle 403 errors (Forbidden Access).

    Args:
        e (Exception): The exception object.

    Returns:
        Rendered HTML template for 403 error and status code 403.
    """
    app.logger.error(f"403 Error: {e}")
    return render_template('403.html'), 403


# Handle 400 Bad Request
@app.errorhandler(400)
def bad_request(e):
    """
    Handle 400 errors (Bad Request).

    Args:
        e (Exception): The exception object.

    Returns:
        Rendered HTML template for 400 error and status code 400.
    """
    app.logger.error(f"400 Error: {e}")
    return render_template('400.html'), 400


# Handle Generic Exceptions (Optional)
@app.errorhandler(Exception)
def handle_exception(e):
    """
    Handle any uncaught exceptions.

    Args:
        e (Exception): The exception object.

    Returns:
        Rendered HTML template for a general error and status code 500.
    """
    app.logger.error(f"Unhandled Exception: {e}")
    return render_template('error.html', error=str(e)), 500


if __name__ == '__main__':
    app.run(port=5001, debug=True)
