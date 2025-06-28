from PIL import Image, ImageFilter
import numpy as np

def generate_video(images, music_path=None, logo_path=None, ending_text=None, size='square'):
    output_filename = f"output_{uuid.uuid4().hex}.mp4"
    output_path = os.path.join('static', 'uploads', output_filename)

    final_clips = []
    for img in images:
        base_clip = ImageClip(img).resize(height=1080 if size == 'story' else 720)

        # ✅ יוצרים גרסה מטושטשת של התמונה באמצעות PIL
        pil_img = Image.open(img)
        blurred_pil = pil_img.filter(ImageFilter.GaussianBlur(10))
        blurred_np = np.array(blurred_pil)
        blurred_bg = (ImageClip(blurred_np)
                      .resize(1.2)
                      .set_duration(2))

        matte_layer = ColorClip(blurred_bg.size, color=(0, 0, 0)).set_opacity(0.2).set_duration(2)

        focused = (base_clip
                   .set_duration(2)
                   .margin(20, color=(0, 0, 0))
                   .set_position("center"))

        composed = CompositeVideoClip([blurred_bg, matte_layer, focused])
        composed = composed.fadein(0.5).fadeout(0.5)
        final_clips.append(composed)

    # המשך הקוד שלך...
