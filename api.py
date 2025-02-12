# from datamanager.sqlite_data_manager import SQLiteDataManager, User, Movie, UserMovieLibrary
from flask import Blueprint, jsonify


api = Blueprint('api', __name__)

@api.route('/users', methods=['GET'])
def get_users():
    # Implementation here
    return jsonify({'message': 'Hello, world!'})



# def list_users():
#     """
#     Fetch and display all users.
#
#     Returns:
#         Rendered HTML template displaying a list of all users.
#     """
#     try:
#         users = data_manager.get_all_users()
#     except Exception as e:
#         app.logger.error(f"Error fetching users: {e}")
#         users = []
#     return render_template('users.html', users=users)