from flask_sqlalchemy import SQLAlchemy
from .data_manager_interface import DataManagerInterface

db = SQLAlchemy()




class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    movies = db.relationship('UserMovieLibrary', backref='user', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            # "email": self.email
        }

    def __str__(self):
        return f"User: {self.name} (ID: {self.id})"

    def __repr__(self):
        return f"User (id={self.id}, name={self.name})"




class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    director = db.Column(db.String, nullable=True)
    year = db.Column(db.String, nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    poster = db.Column(db.String, nullable=True)

    users = db.relationship('UserMovieLibrary', backref='movie', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "director": self.director,
            "year": self.year,
            "rating": self.rating,
        }

    def __str__(self):
        return f"Movie: {self.title} (ID: {self.id}, Director: {self.director}, Year: {self.year})"

    def __repr__(self):
        return (f"Movie (id={self.id}, name={self.title}, "
                f"director={self.director}, year={self.year}, "
                f"rating={self.rating})")




class UserMovieLibrary(db.Model):
    __tablename__ = 'user_movie_library'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    is_favorite = db.Column(db.Boolean, nullable=False, default=False)
    notes = db.Column(db.Text, default='')
    date_added = db.Column(db.DateTime, default=db.func.current_timestamp())
    # date_added = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie'),)

    def __str__(self):
        return (f"Library Entry (User ID: {self.user_id}, Movie ID: {self.movie_id}, "
                f"Favorite: {self.is_favorite}, Date Added: {self.date_added})")

    def __repr__(self):
        return (f"User_Movie_Library (id={self.id}, user_id={self.user_id}, "
                f"movie_id={self.movie_id}, is_favorite={self.is_favorite}, "
                f"notes={self.notes}, date_added={self.date_added})")




class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_file_name):
        self.db = db
        self.db_file_name = db_file_name


    def get_all_users(self):
        try:
            users = User.query.all()
            if not users:
                print("No users found in the database")
                return []
            return users
        except Exception as e:
            print(f"Database query error: {e}")
            return []


    def get_user_movies(self, user_id):

        if not isinstance(user_id, int) or user_id <= 0:
            print("Error: user_id must be a positive integer")
            return False
        try:
            movies = (Movie.query.join(UserMovieLibrary)
                      .filter(UserMovieLibrary.user_id == user_id).all())
            if not movies:
                print("No movies found in the database")
                return []
            return movies

        except Exception as e:
            print(f"Database query error: {e}")
            return []



    def add_user(self, user):
        # Validate the input object
        if not isinstance(user, User):
            print("Error: The provided object is not a User instance")
            return False

        try:
            # Add the user to the database
            self.db.session.add(user)
            self.db.session.commit()

            print('A new user has been successfully added to the database')
            return True

        except Exception as e:
            self.db.session.rollback()  # Rollback on error
            print(f"Error: {e}")
            return False


    def add_movie(self, movie):
        # Validate the input object
        if not isinstance(movie, Movie):
            print("Error: The provided object is not a Movie instance")
            return False

        try:
            # Add the movie to the database
            self.db.session.add(movie)
            self.db.session.commit()

            print("A new movie has been successfully added to the database")
            return True

        except Exception as e:
            self.db.session.rollback()  # Rollback on error
            print(f"Database insertion error: {e}")
            return False


    def update_movie(self, movie):
        # Validate the input object
        if not isinstance(movie, Movie):
            print("Error: The provided object is not a Movie instance")
            return False

        if not movie.id:
            print("Error: Missing movie ID")
            return False

        try:
            # Retrieve the existing movie
            old_movie = Movie.query.get(movie.id)
            if not old_movie:
                print("Error: Movie with the specified ID does not exist")
                return False

            # Update the movie
            self.db.session.delete(old_movie)
            self.db.session.add(movie)
            self.db.session.commit()

            print("The movie has been successfully updated in the database")
            return True

        except Exception as e:
            self.db.session.rollback()  # Rollback on error
            print(f"Database update error: {e}")
            return False


    def update_relationship(self, relationship):
        # Validate the input object
        if not isinstance(relationship, UserMovieLibrary):
            print("Error: The provided object is not a UserMovieLibrary instance")
            return False

        try:
            # Retrieve the existing relationship
            old_relationship = UserMovieLibrary.query.get(relationship.id)
            if not relationship:
                print("Error: Relationship with the specified ID does not exist")
                return False

            # Update the relationship
            self.db.session.delete(old_relationship)
            self.db.session.add(relationship)
            self.db.session.commit()

            print("The relationship has been successfully updated in the database")
            return True

        except Exception as e:
            self.db.session.rollback()  # Rollback on error
            print(f"Database update error: {e}")
            return False


    def delete_movie(self, movie_id):
        # Validate the input type
        if not isinstance(movie_id, int) or movie_id <= 0:
            print("Error: movie_id must be a positive integer")
            return False

        try:
            # Retrieve the movie by ID
            movie = Movie.query.get(movie_id)
            if not movie:
                print(f"Error: No movie found with ID {movie_id}")
                return False

            # Delete the movie
            self.db.session.delete(movie)
            self.db.session.commit()

            print(f"Movie with ID {movie_id} has been successfully deleted from the database")
            return True

        except Exception as e:
            self.db.session.rollback()  # Rollback on error
            print(f"Database deletion error: {e}")
            return False


    def remove_movie_from_user(self, user_id, movie_id):
        # Validate the input type
        if not isinstance(movie_id, int) or movie_id <= 0:
            print("Error: movie_id must be a positive integer")
            return False
        if not isinstance(user_id, int) or user_id <= 0:
            print("Error: user_id must be a positive integer")
            return False

        try:
            relationship = (UserMovieLibrary.query
                            .filter(UserMovieLibrary.user_id == user_id,
                                    UserMovieLibrary.movie_id == movie_id)
                            .first())
            if not relationship:
                print(f"Error: No relationship found with "
                      f"UserID: {user_id} "
                      f"MovieID: {movie_id} ")
                return False

            # Delete the movie
            self.db.session.delete(relationship)
            self.db.session.commit()

            print(f"Relationship with ID {relationship.id} has been successfully deleted from the database")
            return True

        except Exception as e:
            self.db.session.rollback()  # Rollback on error
            print(f"Database deletion error: {e}")
            return False


    def add_user_movie_relationship(self, relationship):
        # Validate the input type
        if not isinstance(relationship, UserMovieLibrary):
            print("Error: The provided object is not a UserMovieLibrary instance")
            return False

        try:
            # Add the relationship to the database
            self.db.session.add(relationship)
            self.db.session.commit()

            print("A new relationship has been successfully added to the database")
            return True

        except Exception as e:
            self.db.session.rollback()  # Rollback on error
            print(f"Database insertion error: {e}")
            return False


    def get_user_by_id(self, user_id):
    # Validate the input type
        if not isinstance(user_id, int) or user_id <= 0:
            print("Error: user_id must be a positive integer")
            return False
        try:
            user = User.query.get(user_id)
            if not user:
                print(f"Error: No user found with ID {user_id}")
                return  False
            return user

        except Exception as e:
            print(f"Database insertion error: {e}")
            return False


    def get_movie_by_id(self, movie_id):
        # Validate the input type
        if not isinstance(movie_id, int) or movie_id <= 0:
            print("Error: movie_id must be a positive integer")
            return False
        try:
            movie = Movie.query.get(movie_id)
            if not movie:
                print(f"Error: No movie found with ID {movie_id}")
                return False
            return movie

        except Exception as e:
            print(f"Database insertion error: {e}")
            return False


    def get_user_movie_relationship(self, user_id,  movie_id):
        # Validate the input type
        if not isinstance(user_id, int) or user_id <= 0:
            print("Error: user_id must be a positive integer")
            return False
        if not isinstance(movie_id, int) or movie_id <= 0:
            print("Error: movie_id must be a positive integer")
            return False
        try:
            relationship = (UserMovieLibrary.query
                            .filter(UserMovieLibrary.user_id == user_id,
                                    UserMovieLibrary.movie_id == movie_id)
                            .first())
            if not relationship:
                print(f"Error: No relationship found with "
                      f"UserID: {user_id} "
                      f"MovieID: {movie_id} ")
                return False
            return relationship

        except Exception as e:
            print(f"Database insertion error: {e}")
            return False