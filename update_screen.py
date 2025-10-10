#!/usr/bin/env python3
import requests
import sys
import json
import os

def login(base_url, username, password):
    """Authenticate and return access token."""
    url = f"{base_url}/login"
    payload = {"login": username, "password": password}
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    data = resp.json()
    token = data.get("access_token")
    if not token:
        raise RuntimeError("Login failed: no access_token in response")
    return token

def update_screen(base_url, token, screen_id, html_file, label=None, name=None, model_id=None):
    """PATCH screen content using access_token."""
    url = f"{base_url}/api/screens/{screen_id}"
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    # Build screen payload according to API reference
    screen_payload = {
        "screen": {
            "content": html_content
        }
    }

    # Optional fields if you want to pass them in later
    if label: screen_payload["screen"]["label"] = label
    if name: screen_payload["screen"]["name"] = name
    if model_id: screen_payload["screen"]["model_id"] = str(model_id)

    resp = requests.patch(url, headers=headers, data=json.dumps(screen_payload))
    resp.raise_for_status()
    print(f"Screen {screen_id} updated successfully.")
    print(resp.json())

def main():
    if len(sys.argv) != 6:
        print("Usage: update_screen.py <base_url> <username> <password> <screen_id> <html_file>")
        sys.exit(1)

    base_url, username, password, screen_id, html_file = sys.argv[1:]

    if not os.path.exists(html_file):
        print(f"Error: file '{html_file}' not found.")
        sys.exit(1)

    try:
        token = login(base_url, username, password)
        update_screen(base_url, token, screen_id, html_file)
    except requests.exceptions.RequestException as e:
        print(f"HTTP error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

