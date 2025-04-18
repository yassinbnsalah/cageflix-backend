import json
RESULTS_FILE = 'cageflix_data/cageflix_data.json'

def get_movies():
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        cageflix_data = json.load(f)
    return cageflix_data



def write_movies(data):
    with open(RESULTS_FILE, 'w') as file:
        json.dump(data, file, indent=4)