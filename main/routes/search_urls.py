
from flask import Blueprint,  jsonify, request
from main.source.json_utils import get_movies
from flask_cors import CORS
from rapidfuzz import fuzz
from dotenv import load_dotenv
load_dotenv()


import os
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


search_bp = Blueprint('search_bp', __name__)
CORS(search_bp)
@search_bp.route('/search', methods=['GET'])
def search_movies():
    cageflix_data = get_movies()
    query = request.args.get("q", "").lower()
    if not query:
        return jsonify([])
    results = []
    for movie in cageflix_data:
        combined_text = f"{movie.get('genres', '')} {movie.get('year', '')} {movie.get('title', '')} {movie.get('description', '')} {movie.get('actors', '')}".lower()

        score = fuzz.partial_ratio(query, combined_text)
        if score > 60:  
            results.append({**movie, "score": score})
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return jsonify(results[:10])  
