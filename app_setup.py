import os
from flask import Flask
from datamanager.sqlite_data_manager import SQLiteDataManager

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