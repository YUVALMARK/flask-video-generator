import os
import uuid
import ffmpeg
from PIL import Image, ImageFilter
import numpy as np

def generate_video(images, music_path=None, logo_path=None, ending_text=None, size='square'):
    output_filename = f"output_{uuid.uuid4().hex}.mp4"
    output_path = os.path.join('static', 'uploads', output_filename)

    width, height = {
        'landscape': (1280, 720),
        'square': (720, 720),
        'story': (720, 1280)
    }.get(size, (720, 720))

    image_clips = []
    for i, img_path in enumerate(images):
        # רקע מטושטש
        img = Image.open(img_path)
        blurred = img.filter(ImageFilter.GaussianBlur(10)).resize((width, height))
        blurred_path = f"{img_path}_blurred_{i}.png"
        blurred.save(blurred_path)

        # התמונה המקורית ממוזערת (מרכז)
        overlay = img.copy()
        overlay.thumbnail((int(width * 0.8), int(height * 0.8)))
        overlay_path = f"{img_path}_overlay_{i}.png"
        overlay_bg = Image.new("RGB", (width, height))
        offset = ((width - overlay.width) // 2, (height - overlay.height) // 2)
        overlay_bg.paste(overlay, offset)
        overlay_bg.save(overlay_path)

        # שמירת תמונה אחת סופית לסרטון
        final_img_path = f"{img_path}_final_{i}.png"
        base = Image.open(blurred_path)
        top = Image.open(overlay_path)
        combined = Image.blend(base, top, alpha=0.9)
        combined.save(final_img_path)
        image_clips.append(final_img_path)

    # יצירת קובץ טקסט עבור התמונות
    with open('inputs.txt', 'w') as f:
        for img in image_clips:
            f.write(f"file '{img}'\n")
            f.write("duration 2\n")

    # פקודת ffmpeg ליצירת הסרטון
    ffmpeg.input('inputs.txt', format='concat', safe=0) \
        .output(output_path, vf=f"scale={width}:{height},fps=24", vcodec='libx264', pix_fmt='yuv420p') \
        .run(overwrite_output=True)

    # הוספת מוזיקה
    if music_path:
        temp_with_audio = output_path.replace(".mp4", "_with_audio.mp4")
        ffmpeg.input(output_path).output(music_path).output(temp_with_audio, vcodec='copy', acodec='aac', shortest=None).run(overwrite_output=True)
        os.replace(temp_with_audio, output_path)

    # הוספת לוגו וטקסט – אופציונלי
    if logo_path or ending_text:
        filters = []
        inputs = [ffmpeg.input(output_path)]

        if logo_path:
            inputs.append(ffmpeg.input(logo_path))
            filters.append(f"[1:v]scale=100:-1[logo];[0:v][logo]overlay=(main_w-overlay_w)/2:20")

        if ending_text:
            filters.append(f"drawtext=text='{ending_text}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,{len(images)*2},{len(images)*2+2})'")

        filtered = ffmpeg.filter_multi_output(inputs, filters) if filters else inputs[0]
        temp_final = output_path.replace(".mp4", "_final.mp4")
        ffmpeg.output(filtered, temp_final).run(overwrite_output=True)
        os.replace(temp_final, output_path)

    return output_path
