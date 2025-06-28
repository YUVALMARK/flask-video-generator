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
        new_path = os.path.join(output_dir, f"frame_{i}.png")
        img.save(new_path)
        resized_images.append(new_path)

    # 🧾 יצירת קובץ inputs.txt
    concat_file = os.path.join(output_dir, "inputs.txt")
    with open(concat_file, "w") as f:
        for img in resized_images:
            filename = os.path.basename(img)
            f.write(f"file '{img}'\n")
            f.write("duration 2\n")

    # ➕ יצירת טקסט סיום כתמונה
    if ending_text:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        img = Image.new('RGB', (width, height), color="white")
        draw = ImageDraw.Draw(img)
        w, h = draw.textsize(ending_text, font=font)
        draw.text(((width - w) / 2, (height - h) / 2), ending_text, fill="black", font=font)
        ending_path = os.path.join(output_dir, "ending.png")
        img.save(ending_path)
        with open(concat_file, "a") as f:
            f.write(f"file '{ending_path}'\n")
            f.write("duration 2\n")

    # 🖼️ יצירת וידאו מהתמונות
    temp_video = os.path.join(output_dir, "temp_video.mp4")
    (
        ffmpeg
        .input(concat_file, format="concat", safe=0)
        .output(temp_video, vcodec="libx264", r=24, pix_fmt="yuv420p")
        .run(overwrite_output=True)
    )

    # 🔊 הוספת מוזיקה (אם קיימת)
    video_with_audio = os.path.join(output_dir, f"output_{uuid.uuid4().hex}.mp4")
    if music_path:
        (
            ffmpeg
            .input(temp_video)
            .input(music_path)
            .output(video_with_audio, vcodec="copy", acodec="aac", shortest=None)
            .run(overwrite_output=True)
        )
    else:
        os.rename(temp_video, video_with_audio)

    # 🏷️ הוספת לוגו (אם קיים)
    if logo_path:
        final_video = os.path.join(output_dir, f"final_{uuid.uuid4().hex}.mp4")
        (
            ffmpeg
            .input(video_with_audio)
            .overlay(ffmpeg.input(logo_path), x='(main_w-overlay_w)/2', y=20, enable='between(t,0,2)')
            .output(final_video)
            .run(overwrite_output=True)
        )
        os.remove(video_with_audio)
        return final_video

    return video_with_audio
