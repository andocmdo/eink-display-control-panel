# E-Ink Display Control Panel

A barebones Flask web application for managing data displayed on a personal E-Ink display.

## Overview

This app provides a simple web interface to manage:
- Weather locations (up to 3)
- Todo items (unlimited, with add/remove/reorder functionality)
- Stock tickers (up to 10)

Data is persisted to `data.json` for use by other scripts that update the E-Ink display.

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML with HTMX for dynamic interactions
- **Data Storage**: JSON file (`data.json`)

## Running the App

```bash
flask run --host=0.0.0.0
```

Or:

```bash
python3 app.py
```

The app will be available at `http://127.0.0.1:5000/`

## File Structure

```
.
├── app.py                      # Main Flask application
├── data.json                   # Persistent data storage (auto-generated)
└── templates/
    ├── index.html              # Main page template
    └── todos_list.html         # Todo list partial (for HTMX updates)
```

## Features

### Weather & Stock Tickers
- Traditional form-based input
- Submit via "Save Weather & Stocks" button
- Data persisted to `data.json`

### Todo Items (HTMX-powered)
- **Add**: Click "Add Todo" to create new todo items
- **Remove**: Click "Remove" button to delete a todo
- **Reorder**: Use ↑/↓ buttons to move todos up or down
- **Auto-save**: Todo text saves automatically when you change it (on blur/change event)
- All operations happen without page reload via HTMX

## Data Structure

### data.json format:

```json
{
  "weather_locations": ["10001", "San Francisco, CA", ""],
  "todos": [
    {
      "id": "uuid-string-here",
      "text": "call mom"
    },
    {
      "id": "another-uuid",
      "text": "buy bananas from grocery"
    }
  ],
  "stock_tickers": ["AAPL", "GOOGL", "TSLA", "", "", "", "", "", "", ""]
}
```

### Todo Items
- Each todo has a unique `id` (UUID) and `text` field
- Order in the array determines display order

## API Endpoints

### Main Routes
- `GET/POST /` - Main page (displays form, saves weather/stocks)

### Todo HTMX Routes
- `GET /todos` - Returns todos list HTML
- `POST /todos/add` - Adds a new empty todo
- `DELETE /todos/<id>/remove` - Removes a todo by ID
- `POST /todos/<id>/update` - Updates todo text
- `POST /todos/<id>/move/up` - Moves todo up in list
- `POST /todos/<id>/move/down` - Moves todo down in list

## Future Enhancements

- [ ] Add same HTMX functionality to weather locations
- [ ] Add same HTMX functionality to stock tickers
- [ ] Add styling/CSS
- [ ] Consider adding user authentication if needed
