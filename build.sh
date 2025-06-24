#!/usr/bin/env bash
echo "🔥 build.sh is running!"
pip install --upgrade pip
pip install -r requirements.txt
python -c "from moviepy.editor import *"
