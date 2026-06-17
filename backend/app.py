import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from models import db
from database import init_db
from routes.auth_routes import auth_bp
from routes.gmail_routes import gmail_bp
from routes.channel_routes import channel_bp
from routes.video_routes import video_bp
from routes.session_routes import session_bp
from routes.notification_routes import notification_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)


def create_app():
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(DATA_DIR, 'db.sqlite3')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False

    CORS(app, origins='*', supports_credentials=True)
    db.init_app(app)
    init_db(app)

    # API blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(gmail_bp, url_prefix='/api/gmails')
    app.register_blueprint(channel_bp, url_prefix='/api/channels')
    app.register_blueprint(video_bp, url_prefix='/api/videos')
    app.register_blueprint(notification_bp, url_prefix='/api/notifications')
    app.register_blueprint(session_bp, url_prefix='/api/sessions')

    # Serve frontend SPA
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path and os.path.exists(os.path.join(FRONTEND_DIR, path)):
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, 'index.html')

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Không tìm thấy'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Lỗi server'}), 500

    return app


app = create_app()
