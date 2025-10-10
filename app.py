from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import uuid
from datetime import datetime

app = Flask(__name__)

DATA_FILE = 'data.json'

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

if __name__ == '__main__':
    app.run(debug=True)
