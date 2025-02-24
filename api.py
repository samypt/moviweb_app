from flask import Blueprint, jsonify
from app_setup import app, data_manager


api = Blueprint('api', __name__)

@api.route('/users', methods=['GET'])
def get_users():
    """
    Fetch and display all users.

    Returns:
        Rendered HTML template displaying a list of all users.
    """
    try:
        users = data_manager.get_all_users()
        users_list = [user.to_dict() for user in users]
    except Exception as e:
        app.logger.error(f"Error fetching users: {e}")
        users_list = []
    return jsonify(users_list)



@api.route("/users/<int:user_id>/movies")
def get_user_movies(user_id):
    """
    Fetch and display the user's movie collection.

    Args:
        user_id (int): ID of the user.

    Returns:
        Rendered HTML template displaying the user's movies.
    """
    # check_user_exist(user_id)
    try:
        movies = data_manager.get_user_movies(user_id)
        movies_list = [movie.to_dict() for movie in movies]
    except Exception as e:
        app.logger.error(f"Error fetching users: {e}")
        movies_list = []
    return jsonify(movies_list)