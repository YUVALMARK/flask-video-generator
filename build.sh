#!/usr/bin/env bash
echo "🚀 build.sh is running!"

# עדכון pip לגרסה האחרונה
pip install --upgrade pip

# התקנת כל הספריות מהקובץ
pip install -r requirements.txt

# בדיקה שהכול תקין (לפי הספרייה שבחרת: ffmpeg-python)
echo "🔍 Checking ffmpeg-python import..."
python -c "import ffmpeg; print('✅ ffmpeg-python imported successfully')"
