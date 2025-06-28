import ffmpeg
import os
import uuid
from PIL import Image, ImageDraw, ImageFont

def generate_video(images, music_path=None, logo_path=None, ending_text=None, size="square"):
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
        img.save(image_path)  # שומר מעל המקורי
        resized_images.append(os.path.abspath(image_path))  # נתיב מלא

    # 🧾 יצירת קובץ inputs.txt
    output_dir = os.path.dirname(resized_images[0]) if resized_images else "static/uploads"
    concat_file = os.path.join(output_dir, "inputs.txt")
    with open(concat_file, "w") as f:
        for img in resized_images:
            f.write(f"file '{img}'\n")
            f.write("duration 2\n")

    # ➕ יצירת טקסט סיום כתמונה (אם יש טקסט סיום)
    if ending_text:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font = ImageFont.truetype(font_path, 60)
        img = Image.new('RGB', (width, height), color="white")
        draw = ImageDraw.Draw(img)
        w, h = draw.textsize(ending_text, font=font)
        draw.text(((width - w) / 2, (height - h) / 2), ending_text, fill="black", font=font)
        ending_path = os.path.join(output_dir, "ending.png")
        img.save(ending_path)
        with open(concat_file, "a") as f:
            f.write(f"file '{os.path.abspath(ending_path)}'\n")
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
        video_input = ffmpeg.input(temp_video)
        audio_input = ffmpeg.input(music_path)
        (
            ffmpeg
            .output(video_input, audio_input, video_with_audio, vcodec="copy", acodec="aac", shortest=None)
            .run(overwrite_output=True)
        )
        os.remove(temp_video)
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
