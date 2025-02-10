import requests
import os
from dotenv import load_dotenv


# load keys
load_dotenv(".env")
API_KEY = os.getenv("API_KEY")


# Constants
HTML_TEMPLATE = "_static/template.html"  # Path to the HTML template file
HTML_PATH = "_static/movies.html"  # Path to save the updated HTML
REPLACEMENT = "__REPLACE__"
BASE_URL = "http://www.omdbapi.com/"  # Base URL for OMDB API


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
            print(data)
            return {
                'title': data['Title'],
                'year': str(data.get('Year', 0)),  # Default to 0 if Year is missing
                'rating': float(data.get('imdbRating', 0.0)),  # Default to 0.0 if imdbRating is missing
                'poster': data.get('Poster', None),  # Default to None if Poster is missing
                'director': data.get('Director', None)  # Default to None if Poster is missing
            }
        else:
            print(f"Error: {data.get('Error', 'Unknown error occurred')}")
            return None
    except requests.RequestException as e:
        print(f"An error occurred while making the API request: {e}")
        return None


def create_html_template(movies):
    """
    Updates an HTML template by replacing a placeholder with movie content.

    Args:
        movies (str): The HTML content to replace the placeholder.

    Returns:
        None
    """
    try:
        # Read the original HTML file
        with open(HTML_TEMPLATE, "r", encoding="utf-8") as file:
            content = file.read()

        # Replace the placeholder with movie content
        content = content.replace(REPLACEMENT, movies)

        # Write the modified HTML back to a file
        with open(HTML_PATH, "w", encoding="utf-8") as file:
            file.write(content)

        print(f"HTML updated and saved to '{HTML_PATH}'")
    except FileNotFoundError:
        print(f"Template file '{HTML_TEMPLATE}' not found.")
    except IOError as e:
        print(f"An error occurred while processing the HTML file: {e}")

