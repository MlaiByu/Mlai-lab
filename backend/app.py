from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from routes import register_routes
from routes.container import restore_running_containers

app = Flask(__name__)
CORS(app, origins=['*'])
app.config.from_object(Config)

register_routes(app)
restore_running_containers()

@app.route('/')
def index():
    return jsonify({"message": "Mlai-Lab API 服务器", "version": "1.0.0"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.SERVER_PORT if hasattr(Config, 'SERVER_PORT') else 9993, debug=False)
