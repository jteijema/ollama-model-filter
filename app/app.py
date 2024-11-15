import os
import json
import time
from flask import Flask, request, jsonify, send_from_directory
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder='static')

MODELS_URL = 'https://ollama.com/search'
CACHE_FILE = 'models_cache.json'
CACHE_EXPIRY = 86400  # 24 hours in seconds


def scrape_models():
    response = requests.get(MODELS_URL)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    models = soup.find_all('li', class_='flex items-baseline border-b border-neutral-200 py-6')

    model_list = []
    for model in models:
        # Extract model name
        name_tag = model.find('h2', class_='truncate text-xl font-medium underline-offset-2 group-hover:underline md:text-2xl')
        name = name_tag.text.strip() if name_tag else "Unknown"

        # Extract model sizes
        size_tags = model.find_all(
            'span',
            class_=lambda c: c and 'bg-[#ddf4ff]' in c and 'text-blue-600' in c
        )
        sizes = [size.text.strip() for size in size_tags]

        # Extract latest update
        updated_tag = model.find('span', {'x-test-updated': True})
        latest_update = updated_tag.text.strip() if updated_tag else "Unknown"

        # Add model data to the list
        model_list.append({'name': name, 'sizes': sizes, 'latest_update': latest_update})

    return model_list


def load_cached_models():
    """
    Load models from the cache if they exist and are not expired.
    """
    if not os.path.exists(CACHE_FILE):
        return None

    with open(CACHE_FILE, 'r') as file:
        cached_data = json.load(file)
        if time.time() - cached_data['timestamp'] < CACHE_EXPIRY:
            return cached_data['models']
    return None


def save_to_cache(models):
    """
    Save models to the cache file with a timestamp.
    """
    with open(CACHE_FILE, 'w') as file:
        json.dump({'models': models, 'timestamp': time.time()}, file)


@app.route('/models', methods=['GET'])
def get_models():
    """
    Serve the models with optional under and over size filtering.
    """
    under_filter = request.args.get('under')  # Get the 'under' size filter
    over_filter = request.args.get('over')  # Get the 'over' size filter

    # Load cached models or scrape if the cache is expired
    models = load_cached_models()
    if models is None:
        models = scrape_models()
        save_to_cache(models)

    # Convert filters to float for comparison
    try:
        under_filter = float(under_filter.lower().replace('b', '').replace('m', '')) if under_filter else None
        over_filter = float(over_filter.lower().replace('b', '').replace('m', '')) if over_filter else None
    except ValueError:
        return jsonify({"error": "Invalid filter format"}), 400

    # Apply filtering if either or both filters are provided
    if under_filter is not None or over_filter is not None:
        filtered_models = []
        for model in models:
            filtered_sizes = []
            for size in model['sizes']:
                # Handle formats like 7x8b
                if 'x' in size:
                    try:
                        parts = size.lower().replace('b', '').replace('m', '').split('x')
                        calculated_size = float(parts[0]) * float(parts[1])
                        if size.endswith('b'):
                            if (under_filter is None or calculated_size <= under_filter) and \
                               (over_filter is None or calculated_size >= over_filter):
                                filtered_sizes.append(size)
                        elif size.endswith('m'):
                            calculated_size /= 1000
                            if (under_filter is None or calculated_size <= under_filter) and \
                               (over_filter is None or calculated_size >= over_filter):
                                filtered_sizes.append(size)
                    except ValueError:
                        continue
                else:
                    # Standard size handling
                    try:
                        numeric_size = float(size.lower().replace('b', '').replace('m', ''))
                        if size.endswith('m'):
                            numeric_size /= 1000
                        if (under_filter is None or numeric_size <= under_filter) and \
                           (over_filter is None or numeric_size >= over_filter):
                            filtered_sizes.append(size)
                    except ValueError:
                        continue

            if filtered_sizes:
                filtered_models.append({
                    'name': model['name'], 
                    'sizes': filtered_sizes,
                    'latest_update': model['latest_update']
                    })

        return jsonify(filtered_models), 200

    # If no filters are applied, return all models
    return jsonify(models), 200


@app.route('/')
def index():
    """
    Serve the frontend index.html.
    """
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static_files(path):
    """
    Serve other static files (e.g., CSS, JS).
    """
    return send_from_directory(app.static_folder, path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
