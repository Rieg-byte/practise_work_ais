from flask import Flask, Response, request, render_template, redirect, url_for, send_from_directory, send_file, jsonify
import os
import cv2
import uuid
from datetime import datetime
import pandas as pd
import threading
from database.sheep_result import SheepResult, db
from model.yolo_sheep import SheepDetector

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
EXPORT_FOLDER = 'exports'
REPORT_FOLDER = 'reports'
HISTORY_FILE = 'history.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EXPORT_FOLDER'] = EXPORT_FOLDER
app.config['REPORT_FOLDER'] = REPORT_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///results.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

detector = SheepDetector()

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return "Файл не загружен", 400

    file = request.files['file']
    if file.filename == '':
        return "Файл не выбран", 400

    filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    input_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    processed_filename = "processed_" + filename
    output_file = os.path.join(app.config['EXPORT_FOLDER'], processed_filename)

    file.save(input_file)

    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image = cv2.imread(input_file)
        result_img, sheep_count = detector.detect_on_image(image)
        cv2.imwrite(output_file, result_img)

    elif filename.lower().endswith(('.mp4', '.avi', '.mov')):
        sheep_count = detector.detect_on_video(input_file, output_file)

    else:
        return "Данный формат файла не поддерживается", 400

    detection = SheepResult(
        timestamp=datetime.now(),
        input_file=filename,
        output_file="processed_" + filename,
        sheep_count=sheep_count
    )
    db.session.add(detection)
    db.session.commit()

    return render_template('result.html',
                           input_file=filename,
                           output_file=processed_filename,
                           sheep_count=sheep_count
                           )

@app.route('/result/upload/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/result/export/<filename>')
def exported_file(filename):
    return send_from_directory(app.config['EXPORT_FOLDER'], filename)

@app.route('/camera')
def camera():
    return render_template('camera.html')


@app.route("/stats")
def stats():
    results = SheepResult.query.order_by(SheepResult.timestamp.desc()).all()
    total_detections = len(results)
    total_sheep = sum(r.sheep_count for r in results)

    return render_template("stats.html",
                           results=results,
                           total_detections=total_detections,
                           total_sheep=total_sheep)



@app.route("/stats/download_report")
def download_full_report():
    results = SheepResult.query.all()
    df = pd.DataFrame([{
        "ID": r.id,
        "Дата и время": r.timestamp,
        "Исходный файл": r.input_file,
        "Обработанный файл": r.output_file,
        "Количество овец": r.sheep_count
    } for r in results])

    filename = f"report_{uuid.uuid4()}.xlsx"
    excel_path = os.path.join(app.config['REPORT_FOLDER'], filename)

    df.to_excel(excel_path, index=False)

    return send_file(excel_path, as_attachment=True)

def gen_frames():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Не удалось открыть камеру")

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            results = detector.detect_on_camera(frame)

            for res in results:
                x_min, y_min, x_max, y_max = int(res['x_min'] * frame.shape[1]), \
                                             int(res['y_min'] * frame.shape[0]), \
                                             int(res['x_max'] * frame.shape[1]), \
                                             int(res['y_max'] * frame.shape[0])
                conf = res['confidence']
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                cv2.putText(frame, f"Sheep {conf:.2f}%", (x_min, y_min - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
