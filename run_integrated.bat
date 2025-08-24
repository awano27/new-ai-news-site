@echo off
chcp 65001 >nul
echo Integrated collection: X articles + RSS feeds...
cd "C:\Users\yoshitaka\new-ai-news-site"
python collect_integrated.py
echo.
echo Integrated collection completed! Please open docs/index.html in browser
pause