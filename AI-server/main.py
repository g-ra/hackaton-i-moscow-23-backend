from flask import Flask, request, send_file, jsonify
import cv2
import numpy as np
from datetime import datetime
import os
import zipfile
from werkzeug.utils import secure_filename

# import photos_predict

app = Flask(__name__)

# Загрузите предварительно обученную модель для детектирования объектов
#net = cv2.dnn.readNetFromCaffe('path/to/caffemodel/prototxt', 'path/to/caffemodel/caffemodel')

UPLOAD_FOLDER = 'uploads'
EXPORT_FOLDER = "export"  # Исправлено на 'export' для единообразия
ZIP_FOLDER = "zip"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)
os.makedirs(ZIP_FOLDER, exist_ok=True)

@app.route('/hello', methods=['GET'])
def hello():
    return 'Hello, World!'

@app.route("/image", methods=["POST"])
def uploadfiles():
    uploaded_files = request.files.getlist("images")
    if not uploaded_files:
        return {"message": "No files provided"}, 400

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    zip_filename = f"annotations{timestamp}.zip"
    zip_path = os.path.join(ZIP_FOLDER, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in uploaded_files:
            if file:  # Проверяем, был ли файл действительно отправлен
                # Используем безопасное имя файла
                safe_filename = secure_filename(file.filename)
                file_path = os.path.join(EXPORT_FOLDER, safe_filename)
                file.save(file_path)  # Сохраняем файл
                zipf.write(file_path, arcname=safe_filename)

    return send_file(zip_path, mimetype="application/octet-stream", as_attachment=True, download_name=zip_filename)

if __name__ == '__main__':
    app.run(debug=True,port=6966)