from flask import Flask, redirect, jsonify, request, render_template
import json
import os
import hmac
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse

app = Flask(__name__)
website_url = 'feketefh.eu'
app.config['SERVER_NAME'] = website_url

def is_api_subdomain():
    return request.host.startswith('api.')
load_dotenv('.env')
PASSWRD = os.environ.get('PASSWORD')
ROUTES_FILE = os.environ.get('ROUTES_FILE')

def load_routes():
    if not os.path.exists(ROUTES_FILE):
        return {}
    with open(ROUTES_FILE, 'r') as f:
        return json.load(f)

def save_routes(routes):
    with open(ROUTES_FILE, 'w') as f:
        json.dump(routes, f, indent=4)

def load_routes_from_json():
    with open("routes.json") as f:
        data = json.load(f)

    routes = {}
    for entry in data.values():
        for route, target in entry.items():
            routes[route] = target
    return routes

@app.route('/', methods=['GET'])
def home():
    if is_api_subdomain():
        return redirect("https://feketefh.eu")
    return render_template('portfolio/index.html')

@app.route('/shorten', methods=['POST'])
def shortenURL():
    if not is_api_subdomain():
        return render_template('404.html'), 404
        
    if not request.is_json:
        return jsonify({"error": "Invalid content type"}), 400

    data = request.get_json()
    required_keys = {"userId", "routename", "redirect", "pass"}
    
    if not required_keys.issubset(data):
        return jsonify({"error": "Missing required fields"}), 400

    if not hmac.compare_digest(data["pass"], PASSWRD):
        return jsonify({"error": "Unauthorized"}), 403

    userId = str(data["userId"])
    routename = data["routename"]
    redirect = data["redirect"]

    routes = load_routes()

    for user_routes in routes.values():
        if routename in user_routes:
            return jsonify({"error": f"Route '{routename}' already exists."}), 409

    if userId not in routes:
        routes[userId] = {}

    routes[userId][routename] = redirect
    save_routes(routes)

    return jsonify({"message": "Route added successfully."}), 201

@app.route('/data/<int:userId>', methods=['GET'])
def getData(userId):
    if not is_api_subdomain():
        return render_template('404.html'), 404
        
    with open('routes.json', 'r') as urlJSON:
        urls = json.load(urlJSON)
    
    strUserId = str(userId)
    if strUserId in urls:
        return jsonify({strUserId: urls[strUserId]})
    else:
        return jsonify({'data': "You don't have any links"})

@app.route('/<path:subpath>', methods=["GET", "POST"])
def dynamic_redirect(subpath):
    if is_api_subdomain():
        return jsonify({"error": "API endpoint not found"}), 404
        
    full_path = f"/{subpath}"
    routes = load_routes_from_json()

    if full_path in routes:
        return redirect(routes[full_path])
    else:
        return render_template('404.html'), 404