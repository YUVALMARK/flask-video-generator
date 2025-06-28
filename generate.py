import os
import uuid
from PIL import Image, ImageFilter

# תיקון לגרסאות Pillow חדשות – ANTIALIAS הועבר ל־Resampling
Image.ANTIALIAS = Image.Resampling.LANCZOS

from moviepy.editor import (
    ImageClip, ColorClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, AudioFileClip
)

# פונקציה שמוסיפה טשטוש לגב התמונה באמצעות GaussianBlur
def blur(get_frame, radius=10):
    def fl(image):
        return Image.fromarray(image).filter(ImageFilter.GaussianBlur(radius))
    return lambda t: fl(get_frame(t))

def generate_video(images, music_path=None, logo_path=None, ending_text=None, size='square'):
    # יצירת שם קובץ ייחודי לפלט
    output_filename = f"output_{uuid.uuid4().hex}.mp4"
    output_path = os.path.join('static', 'uploads', output_filename)

    # ודא שהתיקייה קיימת
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    final_clips = []

    for img in images:
        # יצירת קליפ בסיסי מהתמונה (720 או 1080 לפי הגודל)
        base_clip = ImageClip(img).resize(height=1080 if size == 'story' else 720)

        # יצירת רקע מטושטש מוגדל
        blurred_bg = (
            base_clip
            .resize(1.2)
            .fl(blur(base_clip.get_frame, 10))
            .set_duration(2)
        )

        # שכבת כהות קלה
        matte_layer = ColorClip(blurred_bg.size, color=(0, 0, 0)).set_opacity(0.2).set_duration(2)

        # התמונה המקורית במרכז עם מרווח
        focused = (
            base_clip
            .set_duration(2)
            .margin(20, color=(0, 0, 0))
            .set_position("center")
        )

        # חיבור כל השכבות לקליפ אחד
        composed = CompositeVideoClip([blurred_bg, matte_layer, focused])
        composed = composed.fadein(0.5).fadeout(0.5)
        final_clips.append(composed)

    # חיבור כל הקליפים
    video = concatenate_videoclips(final_clips, method="compose", padding=-0.5)

    # הוספת מוזיקה אם יש
    if music_path:
        audio = AudioFileClip(music_path).subclip(0, video.duration)
        video = video.set_audio(audio)

    # הוספת לוגו אם יש
    if logo_path:
        logo = (
            ImageClip(logo_path)
            .set_duration(video.duration)
            .resize(height=100)
            .set_position(("center", "top"))
        )
        video = CompositeVideoClip([video, logo])

    # הוספת טקסט סיום אם קיים
    if ending_text:
        txt_clip = (
            TextClip(ending_text, fontsize=70, color='white', font='Arial-Bold')
            .set_duration(2)
            .fadein(0.5)
            .set_position('center')
            .set_start(video.duration)
        )
        video = concatenate_videoclips([video, txt_clip])

    # שמירת הווידאו לקובץ
    video.write_videofile(output_path, fps=24)

    return output_path
