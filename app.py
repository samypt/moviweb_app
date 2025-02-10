import omdbapi
import os
from flask import Flask, render_template, request, redirect, url_for
from datamanager.sqlite_data_manager import SQLiteDataManager, User, Movie, UserMovieLibrary


# Define paths for database setup
MAIN_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = "./data"
DB_NAME = "moviwebapp.sqlite"
DB_PATH = os.path.join(MAIN_FOLDER_PATH, DB_PATH, DB_NAME)


# Initialize Flask app
app = Flask(__name__)
data_manager = SQLiteDataManager(DB_PATH)  # Use the appropriate path to your Database


app.secret_key = 'your_secret_key'  # Required for flashing messages
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
data_manager.db.init_app(app)

# Create database if it doesn't exist
if not os.path.exists(DB_PATH):
    with app.app_context():
        data_manager.db.create_all()
        print("New DB Created")


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/users')
def list_users():
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


@app.route("/users/<int:user_id>")
def user_profile(user_id):
    movies = data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', movies=movies, user_id=user_id)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if not request.method == "GET":
        user_name = request.form.get('name')
        user = User(name = user_name)
        data_manager.add_user(user)
        return redirect(url_for('list_users'))
    return render_template("add_user.html")


@app.route("/users/<int:user_id>/add_movie", methods=['GET', 'POST'])
def add_movie(user_id):
    if not request.method == "GET":
        # Add a new movie
        movie_title = request.form.get('title')
        omdb_movie = omdbapi.get_movie_info(movie_title)
        if not omdb_movie:
            return render_template('notification.html',
                                   msg = 'No movie found or an error occurred', user_id=user_id)
        movie = Movie(
            title = omdb_movie['title'],
            year = omdb_movie['year'],
            rating = omdb_movie['rating'],
            poster = omdb_movie['poster'],
            director = omdb_movie['director'],
                      )
        if data_manager.add_movie(movie):
            movie_id = movie.id
            relationship = UserMovieLibrary(user_id=user_id, movie_id=movie_id)
            data_manager.add_user_movie_relationship(relationship)

        # Add new relationship User-Movie


        return redirect(f"/users/{user_id}")
    return render_template("add_movie.html",
                           movies=data_manager.get_user_movies(user_id), user_id=user_id)



@app.route("/users/<int:user_id>/movie/<int:movie_id>", methods=['GET'])
def show_movie(user_id, movie_id):
    movie = data_manager.get_movie_by_id(movie_id)
    relationship = data_manager.get_user_movie_relationship(user_id, movie_id)
    return render_template('movie.html', movie=movie, relationship=relationship )


@app.route("/users/<int:user_id>/update_movie/<int:movie_id>", methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    relationship = data_manager.get_user_movie_relationship(user_id, movie_id)
    movie = data_manager.get_movie_by_id(movie_id)
    if request.method == "GET":
        return render_template('update_movie.html', relationship=relationship, movie=movie)

    movie.title = request.form.get('title')
    movie.director = request.form.get('director')
    movie.year = request.form.get('year')
    movie.rating = request.form.get('rating')
    data_manager.update_movie(movie)

    relationship.notes = request.form.get('notes')
    data_manager.update_relationship(relationship)
    return render_template('notification.html',
                           msg='Movie successfully updated', user_id=user_id)


@app.route("/users/<int:user_id>/delete_movie/<int:movie_id>", methods=['GET'])
def delete_movie(user_id, movie_id):
    data_manager.remove_movie_from_user(user_id, movie_id)
    return render_template('notification.html',
                           msg='Movie successfully deleted', user_id=user_id)


if __name__ == '__main__':
    app.run(port=5001, debug=True)


