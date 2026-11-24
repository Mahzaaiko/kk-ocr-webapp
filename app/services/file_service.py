import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
from config import Config


def is_allowed_extension(filename):
    """Memeriksa apakah ekstensi file termasuk dalam daftar yang diizinkan."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS


def validate_image_file(file_storage):
    """
    Validasi file gambar Kartu Keluarga:
    - Memastikan file ada dan nama berkas tidak kosong.
    - Menolak file PDF secara eksplisit dengan pesan informatif.
    - Menolak ekstensi yang tidak diizinkan (hanya JPG, JPEG, PNG).
    - Memeriksa header berkas menggunakan PIL untuk memastikan berkas benar-benar gambar valid.
    
    Returns:
        (bool, str): (is_valid, error_message_or_success)
    """
    if file_storage is None or file_storage.filename == '':
        return False, "Silakan pilih berkas gambar Kartu Keluarga terlebih dahulu."

    filename = file_storage.filename
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

    # Validasi penolakan PDF secara eksplisit sesuai FR-02 & PRD Bagian 3.2
    if ext == 'pdf':
        return False, "Format file PDF tidak didukung. Harap unggah gambar KK dengan format JPG, JPEG, atau PNG."

    # Validasi format ekstensi
    if ext not in Config.ALLOWED_EXTENSIONS:
        allowed_str = ", ".join(Config.ALLOWED_EXTENSIONS).upper()
        return False, f"Format berkas '{ext}' tidak diizinkan. Hanya berkas {allowed_str} yang diperbolehkan."

    # Validasi integritas berkas gambar menggunakan PIL
    try:
        # Pindahkan pointer stream ke awal
        file_storage.seek(0)
        img = Image.open(file_storage.stream)
        img.verify()  # Verifikasi integritas header gambar
        
        # Format yang diakui PIL: 'JPEG', 'PNG'
        if img.format.lower() not in ['jpeg', 'png']:
            return False, f"Tipe MIME berkas gambar ({img.format}) tidak valid. Harus JPEG atau PNG."

        # Kembalikan pointer stream ke awal setelah dibaca
        file_storage.seek(0)
    except Exception as e:
        return False, f"Berkas yang diunggah rusak atau bukan gambar valid: {str(e)}"

    return True, "Berkas gambar valid."


def save_uploaded_file(file_storage):
    """
    Menyimpan file yang sudah divalidasi ke folder uploads/ dengan nama unik.
    Returns:
        tuple: (saved_filename, full_path)
    """
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    original_filename = secure_filename(file_storage.filename)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    
    # Gunakan UUID prefix agar nama file tidak bertabrakan
    unique_filename = f"{uuid.uuid4().hex[:12]}_{original_filename}"
    file_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
    
    file_storage.save(file_path)
    return unique_filename, file_path
