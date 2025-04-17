from flask import Flask, jsonify, request
import json
from flask_cors import CORS
from rapidfuzz import fuzz
app = Flask(__name__)
CORS(app)
import os

import requests
from flask import Flask, request, jsonify
RESULTS_FILE = 'cage_titles.json'

OMDB_API_KEY = 'b9534972'

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
    url = f"http://www.omdbapi.com/?i={tconst}&apikey={OMDB_API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        if data.get("Response") == "True":
            return jsonify(data), 200
        else:
            return jsonify({"error": "Movie not found in OMDb"}), 404
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