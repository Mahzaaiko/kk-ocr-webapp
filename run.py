from app import create_app
from database.init_db import init_database
from config import Config

app = create_app(Config)


@app.cli.command("init-db")
def init_db_command():
    """Inisialisasi database dan pembuatan tabel dari Flask CLI."""
    success, message = init_database()
    if success:
        print("[SUCCESS] Database berhasil diinisialisasi.")
    else:
        print(f"[FAILED] {message}")


if __name__ == '__main__':
    print(f"[*] Menjalankan Aplikasi OCR Pendataan KK pada http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=Config.DEBUG)
