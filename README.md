# Cageflix Backend

The backend API for Cageflix, a web application that allows users to explore movies and TV shows featuring Nicolas Cage. This API serves processed movie data, including metadata like titles, genres, ratings, and poster URL.



## Setup Instructions

To set up the backend locally:

1. Clone the repository:

    ```bash
    git clone https://github.com/yassinbnsalah/cageflix-backend.git
    cd cageflix-backend
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the application:

    ```bash
    python app.py
    ```

5. Access the API at [http://localhost:5000](http://localhost:5000).

## Docker Support

To run the backend using Docker:

1. Build the Docker image:

    ```bash
    docker build -t cageflix-backend .
    ```

2. Run the Docker container:

    ```bash
    docker run -p 5000:5000 cageflix-backend
    ```

3. Access the API at [http://localhost:5000](http://localhost:5000).

## API Endpoints

- `GET /api/cageflix`: Retrieves a list of movies and TV shows featuring Nicolas Cage.

- `GET /api/cageflix/{imdb_id}`:  Retrieves the details of a specific movie or TV show by its IMDb ID. try this id : tt0134273

- `POST /api/watchlist/{imdb_id}`: Add/Remove a movie or TV show to the user's watchlist using its IMDb ID.

- `GET /api/watchlist`: Retrieves a list of movies and TV shows in the user's watchlist.


