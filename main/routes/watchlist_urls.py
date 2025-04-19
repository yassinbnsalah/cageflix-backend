
from flask import Blueprint, jsonify, request
from main.source.json_utils import get_movies, write_movies
from flask_cors import CORS
watchlist_bp = Blueprint('watchlist_bp', __name__)
CORS(watchlist_bp)
# API to toggle watchlist status of a movie
# This API fetches the data from a local JSON file and updates the watchlist status of the movie
@watchlist_bp.route('/watchlist/<movie_id>', methods=['POST'])
def toggle_watchlist(movie_id):
    movies = get_movies()
    for movie in movies:
        if movie["tconst"] == movie_id:
            movie["watchlisted"] = not movie.get("watchlisted", False)
            write_movies(movies)
            return jsonify({"message": "Watchlist status toggled", "movie": movie}), 200
    return jsonify({"error": "Movie not found"}), 404
# API to get the list of watchlisted movies
# This API fetches the data from a local JSON file and returns the watchlisted movies in a paginated format
@watchlist_bp.route('/watchlist', methods=['GET'])
def get_watchlisted_movies():
    movies = get_movies()
    watchlisted = [m for m in movies if m.get("watchlisted")]

    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 8))
    total = len(watchlisted)

    start = (page - 1) * limit
    end = start + limit
    paginated = watchlisted[start:end]

    return jsonify({
        "results": paginated,
        "page": page,
        "total_pages": (total + limit - 1) // limit
    }), 200

 