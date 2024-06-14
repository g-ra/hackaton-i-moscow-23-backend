from flask import Flask, request, send_file, jsonify
import cv2
import numpy as np
from datetime import datetime
import os
import glob
import zipfile
import logging


import photos_predict
import video_predict as video_predict

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
# Загрузите предварительно обученную модель для детектирования объектов
#net = cv2.dnn.readNetFromCaffe('path/to/caffemodel/prototxt', 'path/to/caffemodel/caffemodel')

UPLOAD_FOLDER = 'uploads'
EXPORT_FOLDER = "export"
ZIP_FOLDER = 'zip'

VIDEO_STORAGE = 'Video_lib'
VIDEO_TEMP = 'Video_temp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)
os.makedirs(ZIP_FOLDER, exist_ok=True)
os.makedirs(VIDEO_STORAGE, exist_ok=True)
os.makedirs(VIDEO_TEMP, exist_ok=True)

def clear_folders(directory):
    for d in directory:

        files = glob.glob(f'{d}/*')
        if files :
                
            for file in files:
                os.remove(file)

@app.route('/hello', methods=['GET'])
def hello():
    return 'Hello, World!'

@app.route("/image", methods=["POST"])
def uploadfiles():

    uploaded_files = request.files.getlist("images")  # Получаем список всех файлов с ключом "images"

    if not uploaded_files:
        return {"message": "No files provided"}, 400

    # Создаем ZIP-архив для сохранения файлов
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    zip_filename = f"annotations_{timestamp}.zip"
    clear_folders([UPLOAD_FOLDER,EXPORT_FOLDER,ZIP_FOLDER])

    for file in uploaded_files:
        if file:  # Проверяем, был ли файл действительно отправлен
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)  # Сохраняем файл

    photos_predict.pics_to_text()

    zip_path = os.path.join(ZIP_FOLDER, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in uploaded_files:
                # Добавляем файл в ZIP-архив
                export_file_path = os.path.join(EXPORT_FOLDER, file.filename[:-3]+"txt")
                print(export_file_path)
                zipf.write(export_file_path, arcname=file.filename[:-3]+"txt")

    # Отправляем архив пользователю
    return send_file(zip_path,mimetype="application/octet-stream", as_attachment=True, download_name=zip_filename)



@app.route("/video", methods=["POST"])
def upload_video():
    try:
        app.logger.debug('1')
        uploaded_files = request.files.getlist("videos")

        if not uploaded_files:
            return {"message": "No files provided"}, 400
        app.logger.debug('2')

        for file in uploaded_files:
            app.logger.debug('3')
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            video_name = f"Video_{hash(file.filename)}_{timestamp}.mp4"
            if file:
                app.logger.debug('4')
                file_path = os.path.join(VIDEO_TEMP, video_name)
                app.logger.debug('5')
                file.save(file_path)
                app.logger.debug('6')
                video_path, json_data = video_predict.process_video_with_compete(input_video_path=file_path, output_video_path=os.path.join(VIDEO_STORAGE, video_name))
                app.logger.debug('7')

        return {"json":json_data, "video_path":'/get_video/'+video_path}, 200
    except Exception as e:
        app.logger.debug(f"An error occurred: {e}")
        return {"message": "An error occurred during video processing"}, 500

@app.route("/get_video/<path:file_path>",methods=["GET"])
def gen_link(file_path):
      app.logger.debug(f"Requested file path: {file_path}")

        # Проверка на недопустимые символы или попытки выхода за пределы директории
      if not file_path or ".." in file_path or file_path.startswith("/"):
        app.logger.error("Invalid file path.")
        abort(400, description="Invalid file path provided.")

      if not os.path.exists(file_path):
              app.logger.error(f"File not found: {file_path}")
              return {"message": "File not found"}, 404
      file_size = os.path.getsize(file_path)
      app.logger.debug(f"File size for {file_path}: {file_size} bytes")


      return send_file(file_path, mimetype="video/mp4",)

if __name__ == '__main__':
    app.run(debug=True,port=6966)