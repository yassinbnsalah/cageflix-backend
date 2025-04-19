
FROM python:3.10-slim

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV OMDB_API_KEY='b9534972'
ENV TMDB_API_KEY="6af42075a27b2ca7c7a5498004a12d4f"
EXPOSE 5000

CMD ["flask", "run"]
