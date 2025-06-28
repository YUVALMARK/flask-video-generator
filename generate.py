import os
import uuid
from PIL import Image  # ✅ ייבוא נכון
Image.ANTIALIAS = Image.Resampling.LANCZOS  # ✅ תיקון לבעיה

from moviepy.editor import (
    ImageClip, ColorClip, TextClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip
)

def generate_video(images, music_path=None, logo_path=None, ending_text=None, size='square'):
    output_filename = f"output_{uuid.uuid4().hex}.mp4"
    output_path = os.path.join('static', 'uploads', output_filename)

    final_clips = []
    for img in images:
        base_clip = ImageClip(img).resize(height=1080 if size == 'story' else 720)
        blurred_bg = (base_clip
                      .resize(1.2)
                      .fx(blur, 10)
                      .set_duration(2))
        matte_layer = ColorClip(blurred_bg.size, color=(0, 0, 0)).set_opacity(0.2).set_duration(2)

        focused = (base_clip
                   .set_duration(2)
                   .margin(20, color=(0, 0, 0))
                   .set_position("center"))

        composed = CompositeVideoClip([blurred_bg, matte_layer, focused])
        composed = composed.fadein(0.5).fadeout(0.5)
        final_clips.append(composed)

    video = concatenate_videoclips(final_clips, method="compose", padding=-0.5)

    if music_path:
        audio = AudioFileClip(music_path).subclip(0, video.duration)
        video = video.set_audio(audio)

    if logo_path:
        logo = (ImageClip(logo_path)
                .set_duration(video.duration)
                .resize(height=100)
                .set_position(("center", "top")))
        video = CompositeVideoClip([video, logo])

    if ending_text:
        txt_clip = (TextClip(ending_text, fontsize=70, color='white', font='Arial-Bold')
                    .set_duration(2)
                    .fadein(0.5)
                    .set_position('center')
                    .set_start(video.duration))
        video = concatenate_videoclips([video, txt_clip])

    video.write_videofile(output_path, fps=24)
    return output_path
