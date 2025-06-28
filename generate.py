import ffmpeg
import os
import uuid
from PIL import Image, ImageDraw, ImageFont

def generate_video(images, music_path=None, logo_path=None, ending_text=None, size="square"):
    output_dir = "static/uploads"
    os.makedirs(output_dir, exist_ok=True)

    # 🧱 הגדרות גודל
    sizes = {
        "square": (720, 720),
        "story": (720, 1280),
        "landscape": (1280, 720)
    }
    width, height = sizes.get(size, (720, 720))

    resized_images = []
    for i, image_path in enumerate(images):
        img = Image.open(image_path).convert("RGB")
        img = img.resize((width, height))
        filename = f"frame_{i}.png"
        new_path = os.path.join(output_dir, filename)
        img.save(new_path)
        resized_images.append(filename)  # רק השם, לא כל הנתיב

    # 🧾 יצירת קובץ inputs.txt
    concat_file = os.path.join(output_dir, "inputs.txt")
    with open(concat_file, "w") as f:
        for filename in resized_images:
            full_path = os.path.join(output_dir, filename)
            f.write(f"file '{full_path}'\n")
            f.write("duration 2\n")

    # ➕ יצירת טקסט סיום כתמונה
    if ending_text:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        img = Image.new('RGB', (width, height), color="white")
        draw = ImageDraw.Draw(img)
        w, h = draw.textsize(ending_text, font=font)
        draw.text(((width - w) / 2, (height - h) / 2), ending_text, fill="black", font=font)
        ending_filename = "ending.png"
        ending_path = os.path.join(output_dir, ending_filename)
        img.save(ending_path)
        with open(concat_file, "a") as f:
            f.write(f"file '{ending_path}'\n")
            f.write("duration 2\n")

    # 🖼️ יצירת וידאו מהתמונות
    temp_video = os.path.join(output_dir, "temp_video.mp4")
    (
        ffmpeg
        .input(concat_file, format="concat", safe=0)
        .output(temp_video, vcodec="libx264", r=24, pix_fm
