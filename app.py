from flask import Flask, jsonify, request
import json
from flask_cors import CORS
from rapidfuzz import fuzz
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
CORS(app)
import os
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
import requests
from flask import Flask, request, jsonify
RESULTS_FILE = 'cage_titles.json'
with open("cageflix_data/cageflix_data.json", "r", encoding="utf-8") as f:
    cageflix_data = json.load(f)



@app.route('/api/cageflix', methods=['GET'])
def get_cageflix_data():
    try:
        json_path = os.path.join('cageflix_data', 'cageflix_data.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        start = (page - 1) * limit
        end = start + limit

        paginated_data = data[start:end]

        return jsonify({
            'page': page,
            'limit': limit,
            'total': len(data),
            'total_pages': (len(data) + limit - 1) // limit,
            'results': paginated_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/cageflix/<tconst>", methods=["GET"])
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


@app.route("/api/search", methods=["GET"])
def search_movies():
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


if __name__ == '__main__':
    app.run(debug=True)