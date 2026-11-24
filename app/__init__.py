import os
import time
from flask import Flask, send_from_directory, flash, redirect, url_for
from config import Config


def create_app(config_class=Config):
    """Application Factory untuk menginisialisasi aplikasi Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Pastikan direktori uploads tersedia
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Registrasi Blueprints
    from app.controllers import main_bp
    app.register_blueprint(main_bp)

    # Context processor untuk cache-busting otomatis pada file CSS/JS
    @app.context_processor
    def inject_asset_version():
        return {'asset_version': int(time.time())}

    # Header anti-cache untuk aset statis selama tahap pengembangan
    @app.after_request
    def add_header(response):
        if app.config.get('DEBUG', False):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    # Route untuk menampilkan file yang diunggah
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Error handler untuk berkas yang melebihi batas ukuran 16MB (HTTP 413)
    @app.errorhandler(413)
    def request_entity_too_large(error):
        flash("Ukuran berkas melebihi batas maksimum 16MB. Harap perkecil ukuran gambar KK Anda.", "danger")
        return redirect(url_for('main.index'))

    return app
