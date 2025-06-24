from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
from generate import generate_video

app = Flask(__name__, template_folder="templates")
CORS(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ✅ דף הבית – יציג index.html מהתיקייה templates
@app.route('/')
def index():
    return render_template("index.html")

# ✅ יצירת סרטון
@app.route('/create-video', methods=['POST'])
def create_video_route():
    if 'images' not in request.files:
        return jsonify({'error': 'No images uploaded'}), 400

    image_files = request.files.getlist('images')
    music_file = request.files.get('music')
    logo_file = request.files.get('logo')
    ending_text = request.form.get('ending_text')
    size = request.form.get('size')

    image_paths = []
    for img in image_files:
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], img.filename)
        img.save(img_path)
        image_paths.append(img_path)

    music_path = None
    if music_file:
        music_path = os.path.join(app.config['UPLOAD_FOLDER'], music_file.filename)
        music_file.save(music_path)

    logo_path = None
    if logo_file:
        logo_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_file.filename)
        logo_file.save(logo_path)

    output_path = generate_video(image_paths, music_path, logo_path, ending_text, size)
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
