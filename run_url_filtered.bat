@echo off
chcp 65001 >nul
echo URL filter method for X article collection...
cd "C:\Users\yoshitaka\new-ai-news-site"
python collect_url_filtered.py
echo.
echo Collection completed! Please open docs/index.html in browser
pause