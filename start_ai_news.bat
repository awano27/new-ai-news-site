@echo off
echo ======================================
echo    Daily AI News - 自動実行
echo ======================================
echo.

cd /d "%~dp0"

echo 📰 AIニュースサイトを生成中...
python run_simple_news.py

echo.
echo ✅ 完了！何かキーを押してください...
pause