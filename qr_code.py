import qrcode
import os

def create_qr(url, SESSION_PATH):
    file_name = "QRcode.png"
    full_path = os.path.join(SESSION_PATH, file_name)
    img = qrcode.make(url)

    img.save(full_path)
