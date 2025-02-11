import requests
import os
from dotenv import load_dotenv


# load keys
load_dotenv(".env")
API_KEY = os.getenv("API_KEY")


# Constants
BASE_URL = "http://www.omdbapi.com/"  # Base URL for OMDB API


def safe_get(data, key, default=None):
    """
    Safely retrieves a value from a dictionary, replacing "N/A" with a default value.
    """
    value = data.get(key, default)
    return default if value == "N/A" else value


def get_movie_info(title):
    """
    Fetches movie information from the OMDB API based on the given title.

    Args:
        title (str): Title of the movie to search for.

    Returns:
        dict: A dictionary containing movie details with keys:
            - 'title' (str): Movie title.
            - 'year' (int): Release year.
            - 'rating' (float): IMDb rating.
            - 'poster' (str): URL of the movie poster.
        None: If the movie is not found or an error occurs.
    """
    # Parameters for the request
    params = {
        "t": title.strip(),
        "apikey": API_KEY
    }

    try:
        # Make the request
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        data = response.json()

        # Validate the API response
        if data.get("Response") == "True":
            return {
                'title': safe_get(data, 'Title', 'Unknown Title'),
                'year': safe_get(data, 'Year', '0'),
                'rating': float(safe_get(data, 'imdbRating', 0.0)),
                'poster': safe_get(data, 'Poster', None),
                'director': safe_get(data, 'Director', 'Unknown Director')
            }
        else:
            print(f"Error: {data.get('Error', 'Unknown error occurred')}")
            return None
    except requests.RequestException as e:
        print(f"An error occurred while making the API request: {e}")
        return None

