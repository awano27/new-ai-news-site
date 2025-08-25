@echo off
setlocal
cd /d "%~dp0\docs"
echo Starting local server at http://127.0.0.1:8080

where py >nul 2>nul
if not errorlevel 1 (
  py -3 -m http.server 8080
  goto end
)

where python >nul 2>nul
if not errorlevel 1 (
  python -m http.server 8080
  goto end
)

echo Python not found. If Node is installed, you can run:
echo   npx http-server . -p 8080 -s

:end
endlocal
