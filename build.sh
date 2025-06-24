#!/usr/bin/env bash
set -e  # עוצר אם יש שגיאה

echo "🔥 build.sh is running!"
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
