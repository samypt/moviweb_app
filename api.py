# from datamanager.sqlite_data_manager import SQLiteDataManager, User, Movie, UserMovieLibrary
from flask import Blueprint, jsonify
from app_setup import data_manager


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
        print(users)
        # users = []
    except Exception as e:

        print(f"Error fetching users: {e}")
        users = []
    return jsonify(users)
