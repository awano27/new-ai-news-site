@echo off
echo Collecting X articles from Google Spreadsheet...
cd "C:\Users\yoshitaka\new-ai-news-site"
python collect_simple_2025.py
echo.
echo Collection completed! Please refresh your browser.
pause