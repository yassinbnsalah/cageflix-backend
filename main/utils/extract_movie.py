from flask import Flask, jsonify, request
import json

from flask_cors import CORS
from rapidfuzz import fuzz
app = Flask(__name__)
CORS(app)
import os
from dotenv import load_dotenv
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
from utils.extract_id_nico import get_nicolas_cage_nconst
RESULTS_FILE = 'cage_titles.json'
import gzip
import csv

    
import requests
from flask import Flask,jsonify


def get_cage_titles_simple():
    nconst = get_nicolas_cage_nconst()
    if not nconst:
        return {'error': 'Nicolas Cage not found in the dataset'}
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            data = json.load(f)
            if nconst in data:
                return {'tconsts': data[nconst]}
            
    filepath = 'datasets/title.principals.tsv.gz'
    tconsts = set()

    try:
        with gzip.open(filepath, 'rt', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if row['nconst'] == nconst and row['category'] in ['actor', 'self']:
                    tconsts.add(row['tconst'])

        if tconsts:
            os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
            with open(RESULTS_FILE, 'w') as f:
                json.dump({nconst: list(tconsts)}, f)

            return {'tconsts': list(tconsts)}
        else:
            return {'error': 'No titles found for this nconst'}

    except Exception as e:
        return {'error': str(e)}


@app.route('/api/cage-title-info', methods=['GET'])
def get_title_info_api():
    tconsts_file = 'cageflix_data/cage_titles.json'
    basics_filepath = 'datasets/title.basics.tsv.gz'
    output_file = 'cageflix_data/cage_title_info2.json'

    try:

        if not os.path.exists(tconsts_file):
            return jsonify({'error': 'tconsts cache file not found'}), 404

        with open(tconsts_file, 'r') as f:
            data = json.load(f)

        if not data:
            return jsonify({'error': 'No tconsts found in cache'}), 404

        nconst = list(data.keys())[0]
        tconsts = set(data[nconst])

 
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
                        'poster': movie_data.get('Poster'),
                        'description': movie_data.get('Plot'),
                        'rating': movie_data.get('imdbRating'),
                        'actors': movie_data.get('Actors'),
                        'directors': movie_data.get('Director'),
                    })

        if not movies:
            return jsonify({'message': 'No title info found for the given tconsts'}), 404


        with open(output_file, 'w', encoding='utf-8') as out_f:
            json.dump(movies, out_f, indent=2)

        return jsonify({'movies': movies}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500