from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from generate import generate_video

app = Flask(__name__, template_folder="templates")
CORS(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ✅ יצירת התיקייה אם לא קיימת
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ דף הבית – יציג את index.html מהתיקייה templates
@app.route('/')
def index():
    return render_template("index.html")

# ✅ נתיב POST ליצירת הסרטון
@app.route('/create-video', methods=['POST'])
def create_video_route():
    if 'images' not in request.files:
        return jsonify({'error': 'No images uploaded'}), 400

    image_files = request.files.getlist('images')
    music_file = request.files.get('music')
    logo_file = request.files.get('logo')
    ending_text = request.form.get('ending_text')
    size = request.form.get('size')

    # ⬇️ שמירת התמונות
    image_paths = []
    for img in image_files:
        filename = secure_filename(img.filename)
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img.save(img_path)
        image_paths.append(img_path)

    # ⬇️ שמירת מוזיקה (אם קיימת)
    music_path = None
    if music_file:
        filename = secure_filename(music_file.filename)
        music_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        music_file.save(music_path)

    # ⬇️ שמירת לוגו (אם קיים)
    logo_path = None
    if logo_file:
        filename = secure_filename(logo_file.filename)
        logo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logo_file.save(logo_path)

    # ✅ יצירת הסרטון באמצעות הפונקציה מהקובץ generate.py
    output_path = generate_video(image_paths, music_path, logo_path, ending_text, size)

    # ✅ שליחת הסרטון להורדה
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
