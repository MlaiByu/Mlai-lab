from flask import Flask, jsonify
from flask_cors import CORS
import os

from config import Config
from utils.db import init_db
from routes import register_routes

app = Flask(__name__)
CORS(app, origins=['*'])

app.config.from_object(Config)

init_db()

register_routes(app)

@app.route('/')
def index():
    return jsonify({"message": "Mlai-Lab API 服务器", "version": "1.0.0"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
