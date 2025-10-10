from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import uuid
from datetime import datetime
import random
import requests

app = Flask(__name__)

DATA_FILE = 'data.json'

# E-ink server configuration - load from environment variables
EINK_BASE_URL = os.getenv('EINK_BASE_URL', '')
EINK_USERNAME = os.getenv('EINK_USERNAME', '')
EINK_PASSWORD = os.getenv('EINK_PASSWORD', '')
EINK_SCREEN_ID = os.getenv('EINK_SCREEN_ID', '')

def load_data():
    """Load data from JSON file, return default structure if file doesn't exist"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return {
            'weather': [],
            'todos': [],
            'stocks': []
        }

def save_data(data):
    """Save data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def fetch_stock_prices(tickers):
    """Fetch stock prices from AlphaVantage API (placeholder with dummy data)

    Args:
        tickers: List of stock ticker symbols

    Returns:
        Dictionary mapping ticker symbols to prices (as strings)
    """
    # TODO: Implement actual AlphaVantage bulk quote API call
    # For now, return dummy prices for each ticker
    prices = {}
    for ticker in tickers:
        prices[ticker] = str(round(random.uniform(50, 500), 2))
    return prices

def fetch_weather_temperature(location):
    """Fetch temperature for location from weather API (placeholder with dummy data)

    Args:
        location: Location string (zip code or city, state)

    Returns:
        Temperature as string
    """
    # TODO: Implement actual weather API call
    # For now, return dummy temperature
    dummy_temp = random.randint(32, 95)
    return str(dummy_temp)

def eink_login(base_url, username, password):
    """Authenticate to e-ink server and return access token"""
    url = f"{base_url}/login"
    payload = {"login": username, "password": password}
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    data = resp.json()
    token = data.get("access_token")
    if not token:
        raise RuntimeError("Login failed: no access_token in response")
    return token

def eink_update_screen(base_url, token, screen_id, html_content):
    """Update e-ink screen content via PATCH request"""
    url = f"{base_url}/api/screens/{screen_id}"

    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    screen_payload = {
        "screen": {
            "content": html_content
        }
    }

    resp = requests.patch(url, headers=headers, data=json.dumps(screen_payload))
    resp.raise_for_status()
    return resp.json()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = load_data()

        # Collect weather data - preserve existing temperatures
        weather = []
        for i in range(3):
            location = request.form.get(f'weather_{i}', '').strip()
            if location:
                # Find existing temperature if this location was already saved
                existing_temp = ''
                for w in data.get('weather', []):
                    if w['location'] == location:
                        existing_temp = w.get('temperature', '')
                        break
                weather.append({'location': location, 'temperature': existing_temp})

        # Collect stock data - preserve existing prices
        stocks = []
        for i in range(10):
            ticker = request.form.get(f'stock_{i}', '').strip()
            if ticker:
                # Find existing price if this ticker was already saved
                existing_price = ''
                for s in data.get('stocks', []):
                    if s['ticker'] == ticker:
                        existing_price = s.get('price', '')
                        break
                stocks.append({'ticker': ticker, 'price': existing_price})

        data['weather'] = weather
        data['stocks'] = stocks
        save_data(data)

        return redirect(url_for('index'))

    # GET request - load and display current data
    data = load_data()
    return render_template('index.html', data=data)

# Todo HTMX routes
@app.route('/todos', methods=['GET'])
def get_todos():
    """Return the todos list HTML"""
    data = load_data()
    return render_template('todos_list.html', todos=data['todos'])

@app.route('/todos/add', methods=['POST'])
def add_todo():
    """Add a new todo item"""
    data = load_data()
    new_todo = {
        'id': str(uuid.uuid4()),
        'text': ''
    }
    data['todos'].append(new_todo)
    save_data(data)
    return render_template('todos_list.html', todos=data['todos'])

@app.route('/todos/<todo_id>/remove', methods=['DELETE'])
def remove_todo(todo_id):
    """Remove a todo item"""
    data = load_data()
    data['todos'] = [t for t in data['todos'] if t['id'] != todo_id]
    save_data(data)
    return render_template('todos_list.html', todos=data['todos'])

@app.route('/todos/<todo_id>/update', methods=['POST'])
def update_todo(todo_id):
    """Update a todo item's text"""
    data = load_data()
    text = request.form.get('text', '')
    for todo in data['todos']:
        if todo['id'] == todo_id:
            todo['text'] = text
            break
    save_data(data)
    return ''

@app.route('/todos/<todo_id>/move/<direction>', methods=['POST'])
def move_todo(todo_id, direction):
    """Move a todo up or down"""
    data = load_data()
    todos = data['todos']

    # Find the index of the todo
    index = next((i for i, t in enumerate(todos) if t['id'] == todo_id), None)

    if index is not None:
        if direction == 'up' and index > 0:
            todos[index], todos[index - 1] = todos[index - 1], todos[index]
        elif direction == 'down' and index < len(todos) - 1:
            todos[index], todos[index + 1] = todos[index + 1], todos[index]

    save_data(data)
    return render_template('todos_list.html', todos=data['todos'])

@app.route('/preview')
def preview():
    """Preview page showing E-ink display format"""
    data = load_data()

    # Get current date
    now = datetime.now()
    day_name = now.strftime('%A')
    date_str = now.strftime('%B %d, %Y')

    return render_template('preview.html',
                         day=day_name,
                         date=date_str,
                         weather=data.get('weather', []),
                         todos=data.get('todos', []),
                         stocks=data.get('stocks', []))

# Update endpoints for cron jobs
@app.route('/update/stocks', methods=['GET'])
def update_stocks():
    """Update stock prices from API"""
    data = load_data()
    stocks = data.get('stocks', [])

    if not stocks:
        return jsonify({'status': 'success', 'message': 'No stocks to update', 'updated': 0})

    # Get list of tickers
    tickers = [stock['ticker'] for stock in stocks]

    # Fetch prices from API (bulk call)
    prices = fetch_stock_prices(tickers)

    # Update prices in data
    updated_count = 0
    for stock in stocks:
        if stock['ticker'] in prices:
            stock['price'] = prices[stock['ticker']]
            updated_count += 1

    save_data(data)

    return jsonify({
        'status': 'success',
        'message': f'Updated {updated_count} stock prices',
        'updated': updated_count,
        'stocks': stocks
    })

@app.route('/update/weather', methods=['GET'])
def update_weather():
    """Update weather temperatures from API"""
    data = load_data()
    weather = data.get('weather', [])

    if not weather:
        return jsonify({'status': 'success', 'message': 'No weather locations to update', 'updated': 0})

    # Update temperature for each location
    updated_count = 0
    for location_data in weather:
        location = location_data['location']
        temperature = fetch_weather_temperature(location)
        location_data['temperature'] = temperature
        updated_count += 1

    save_data(data)

    return jsonify({
        'status': 'success',
        'message': f'Updated {updated_count} weather locations',
        'updated': updated_count,
        'weather': weather
    })

@app.route('/update/display', methods=['GET'])
def update_display():
    """Render preview HTML and upload to e-ink display server"""
    # Check if e-ink server is configured
    if not all([EINK_BASE_URL, EINK_USERNAME, EINK_PASSWORD, EINK_SCREEN_ID]):
        return jsonify({
            'status': 'error',
            'message': 'E-ink server not configured. Set EINK_BASE_URL, EINK_USERNAME, EINK_PASSWORD, and EINK_SCREEN_ID environment variables.'
        }), 500

    try:
        # Load data
        data = load_data()

        # Get current date
        now = datetime.now()
        day_name = now.strftime('%A')
        date_str = now.strftime('%B %d, %Y')

        # Render the preview template to HTML string
        html_content = render_template('preview.html',
                                     day=day_name,
                                     date=date_str,
                                     weather=data.get('weather', []),
                                     todos=data.get('todos', []),
                                     stocks=data.get('stocks', []))

        # Login to e-ink server
        token = eink_login(EINK_BASE_URL, EINK_USERNAME, EINK_PASSWORD)

        # Update the screen
        response = eink_update_screen(EINK_BASE_URL, token, EINK_SCREEN_ID, html_content)

        return jsonify({
            'status': 'success',
            'message': f'Display updated successfully for screen {EINK_SCREEN_ID}',
            'screen_id': EINK_SCREEN_ID,
            'server_response': response
        })

    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'HTTP error communicating with e-ink server: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error updating display: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
