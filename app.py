from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
CORS(app)

import os
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

from main.routes.movies_urls import movie_bp
from main.routes.search_urls import search_bp
from main.routes.watchlist_urls import watchlist_bp
app.register_blueprint(movie_bp, url_prefix='/api')   
app.register_blueprint(search_bp, url_prefix='/api')   
app.register_blueprint(watchlist_bp, url_prefix='/api')  
if __name__ == '__main__':
    app.run(debug=True)