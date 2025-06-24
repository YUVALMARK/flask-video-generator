#!/usr/bin/env bash
echo "🚀 build.sh is running!"

# עדכון pip לגרסה האחרונה
pip install --upgrade pip

# התקנת כל הספריות מהקובץ
pip install -r requirements.txt

# בדיקה שההתקנה של moviepy הצליחה
echo "🔍 Checking moviepy import..."
python -c "from moviepy.editor import *"
