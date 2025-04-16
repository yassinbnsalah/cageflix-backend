from flask import Flask, jsonify, request
import json

from flask_cors import CORS

app = Flask(__name__)
CORS(app)
import os

RESULTS_FILE = 'cage_titles.json'
import gzip
import csv
with open("cageflix_data/cageflix_data.json", "r", encoding="utf-8") as f:
    cageflix_data = json.load(f)
@app.route('/api/nicolas-cage/nconst', methods=['GET'])
def get_nicolas_cage_nconst():
    filepath = 'datasets/name.basics.tsv.gz' 
    try:
        with gzip.open(filepath, 'rt', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if row['primaryName'].lower() == 'nicolas cage':
                    return jsonify({
                        'nconst': row['nconst'],
                        'name': row['primaryName']
                    })
        return jsonify({'error': 'Nicolas Cage not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


def get_nicolas_cage_nconst(filepath="datasets/name.basics.tsv.gz"):
    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row['primaryName'] == 'Nicolas Cage':
                return row['nconst']
@app.route('/api/get-cage-titles', methods=['GET'])
def get_cage_titles():
    # Get the 'nconst' from the function
    nconst = get_nicolas_cage_nconst()
    if not nconst:
        return jsonify({'error': 'Nicolas Cage not found in the dataset'}), 404
    
    # Check if the results file already exists
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            data = json.load(f)
            if nconst in data:
                return jsonify({'tconsts': data[nconst]}), 200
    
    filepath = 'datasets/title.principals.tsv.gz'
    tconsts = set()

    try:
        with gzip.open(filepath, 'rt', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if row['nconst'] == nconst and row['category'] in ['actor', 'self']:
                    print(row['tconst'])
                    tconsts.add(row['tconst'])

        if tconsts:
            # Save the result in the JSON file for future use
            with open(RESULTS_FILE, 'w') as f:
                data = {nconst: list(tconsts)}
                json.dump(data, f)
            
            return jsonify({'tconsts': list(tconsts)}), 200
        else:
            return jsonify({'error': 'No titles found for this nconst'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
import requests
from flask import Flask, request, jsonify

OMDB_API_KEY = 'b9534972'
@app.route('/api/cage-title-info', methods=['GET'])
def get_title_info_api():
    tconsts_file = 'cage_titles.json'
    basics_filepath = 'datasets/title.basics.tsv.gz'
    output_file = 'cage_title_info2.json'

    try:
        # Step 1: Load tconsts from JSON cache
        if not os.path.exists(tconsts_file):
            return jsonify({'error': 'tconsts cache file not found'}), 404

        with open(tconsts_file, 'r') as f:
            data = json.load(f)

        if not data:
            return jsonify({'error': 'No tconsts found in cache'}), 404

        nconst = list(data.keys())[0]
        tconsts = set(data[nconst])

        # Step 2: Parse title.basics.tsv.gz
        movies = []
        with gzip.open(basics_filepath, 'rt', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if row['tconst'] in tconsts and row['titleType'] in ['movie', 'tvMovie', 'tvSeries']:
                    print("movie:", row['primaryTitle'])
                    url = f"http://www.omdbapi.com/?i={row['tconst']}&apikey={OMDB_API_KEY}"
                    response = requests.get(url)
                    movie_data = response.json()
                    print(movie_data.get('Poster'))
                    movies.append({
                        'tconst': row['tconst'],
                        'title': row['primaryTitle'],
                        'year': row['startYear'],
                        'genres': row['genres'],
                        'runtime': row['runtimeMinutes'],
                        'poster': movie_data.get('Poster')
                    })

        if not movies:
            return jsonify({'message': 'No title info found for the given tconsts'}), 404

        # Step 3: Save result to JSON file
        with open(output_file, 'w', encoding='utf-8') as out_f:
            json.dump(movies, out_f, indent=2)

        return jsonify({'movies': movies}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cageflix', methods=['GET'])
def get_cageflix_data():
    try:
        json_path = os.path.join('cageflix_data', 'cageflix_data.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Get page & limit query params
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
if __name__ == '__main__':
    app.run(debug=True)