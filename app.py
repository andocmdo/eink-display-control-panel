from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

DATA_FILE = 'data.json'

def load_data():
    """Load data from JSON file, return default structure if file doesn't exist"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return {
            'weather_locations': ['', '', ''],
            'todo_items': [''] * 10,
            'stock_tickers': [''] * 10
        }

def save_data(data):
    """Save data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Collect weather locations
        weather_locations = [
            request.form.get(f'weather_{i}', '') for i in range(3)
        ]

        # Collect todo items
        todo_items = [
            request.form.get(f'todo_{i}', '') for i in range(10)
        ]

        # Collect stock tickers
        stock_tickers = [
            request.form.get(f'stock_{i}', '') for i in range(10)
        ]

        # Save to file
        data = {
            'weather_locations': weather_locations,
            'todo_items': todo_items,
            'stock_tickers': stock_tickers
        }
        save_data(data)

        return redirect(url_for('index'))

    # GET request - load and display current data
    data = load_data()
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
