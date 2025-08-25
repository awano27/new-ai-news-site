@echo off
setlocal
cd /d "%~dp0"
echo ======================================
echo   Daily AI News - Integrated Collect (X+RSS)
echo   Only last 48h / Ensure >=20 items
echo ======================================
echo.

set "PYTHON="
where py >nul 2>nul
if not errorlevel 1 (
  set "PYTHON=py -3"
) else (
  where python >nul 2>nul
  if not errorlevel 1 (
    set "PYTHON=python"
  ) else (
    echo Python が見つかりませんでした。Python 3 をインストールしてください。
    goto :end
  )
)

echo STEP 1) Install Python deps (feedparser, requests)
%PYTHON% -m pip install --upgrade pip >nul 2>nul
%PYTHON% -m pip install feedparser requests
if errorlevel 1 goto :err

echo STEP 2) Run integrated build (scripts\integrated_build.py)
%PYTHON% scripts\integrated_build.py
if errorlevel 1 goto :err

echo STEP 3) Run acceptance tests (incl. freshness)
node scripts\tests\verify_acceptance.js
if errorlevel 1 goto :err

echo.
echo DONE. Use serve_docs.bat to preview locally.
goto :end

:err
echo.
echo ERROR. See logs above.
exit /b 1

:end
endlocal
