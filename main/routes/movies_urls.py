from flask import Blueprint, jsonify, request
import json
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

import os
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
import requests




movie_bp = Blueprint('movie_bp', __name__)
CORS(movie_bp) 
@movie_bp.route('/cageflix', methods=['GET'])
def get_movies_data():
    try:
        json_path = os.path.join('cageflix_data', 'cageflix_data.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for item in data:
            year = item.get('year')
            if isinstance(year, str):
                try:
                    item['year'] = int(year)
                except ValueError:
                    item['year'] = 0 
        filtered_data = [
            item for item in data if int(item.get('year', 0)) <= 2025
        ]
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        sorted_data = sorted(filtered_data, key=lambda x: int(x.get('year', 0)), reverse=True)

        start = (page - 1) * limit
        end = start + limit

        filtered_dataRating = [
            item for item in sorted_data
            if int(item.get('year', 0)) <= 2025 and item.get('rating') and item['rating'] != 'N/A'
        ]


        sorted_movieRated = sorted(filtered_dataRating, key=lambda x: float(x['rating'][0]), reverse=True)

        top_rated_movies = sorted_movieRated[:4]
        paginated_data = sorted_data[start:end]
        return jsonify({
            'page': page,
            'top_rated_movies': top_rated_movies,
            'limit': limit,
            'total': len(sorted_data),
            'total_pages': (len(sorted_data) + limit - 1) // limit,
            'results': paginated_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@movie_bp.route('/cageflix/<tconst>', methods=['GET'])
def get_movie_detail(tconst):
    omdb_url = f"http://www.omdbapi.com/?i={tconst}&apikey={OMDB_API_KEY}"
    tmdb_url = f"https://api.themoviedb.org/3/find/{tconst}?api_key={TMDB_API_KEY}&external_source=imdb_id"

    try:
        omdb_response = requests.get(omdb_url)
        omdb_data = omdb_response.json()

        tmdb_response = requests.get(tmdb_url)
        tmdb_data = tmdb_response.json()

        if omdb_data.get("Response") != "True":
            return jsonify({"error": "Movie not found in OMDb"}), 404

        movie_results = tmdb_data.get("movie_results", [])
        tmdb_id = movie_results[0]["id"] if movie_results else None

        trailers = []
        if tmdb_id:
            videos_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/videos?api_key={TMDB_API_KEY}"
            videos_response = requests.get(videos_url)
            videos_data = videos_response.json()
            trailers = [
                {
                    "name": v["name"],
                    "site": v["site"],
                    "type": v["type"],
                    "key": v["key"],
                    "url": f"https://www.youtube.com/watch?v={v['key']}" if v["site"] == "YouTube" else None
                }
                for v in videos_data.get("results", []) if v["type"] == "Trailer"
            ]

        result = {
            "title": omdb_data.get("Title"),
            "year": omdb_data.get("Year"),
            "rated": omdb_data.get("imdbRating"),
            "released": omdb_data.get("Released"),
            "runtime": omdb_data.get("Runtime"),
            "genre": omdb_data.get("Genre"),
            "director": omdb_data.get("Director"),
            "writer": omdb_data.get("Writer"),
            "actors": omdb_data.get("Actors"),
            "plot": omdb_data.get("Plot"),
            "language": omdb_data.get("Language"),
            "poster": omdb_data.get("Poster"),
            "ratings": omdb_data.get("Ratings"),
            "tmdb_id": tmdb_id,
            "trailers": trailers,
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
