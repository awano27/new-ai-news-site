@echo off
setlocal
cd /d "%~dp0"
echo Installing dependencies (first time only)...
call npm install
if errorlevel 1 goto :err

echo Running link/meta audits...
node scripts/audit/links.js || goto :err
node scripts/audit/html.js || goto :err

echo To run axe/lighthouse locally, start a server first:
echo   serve_docs.bat  (opens http://127.0.0.1:8080)
echo Then in another terminal run:
echo   npm run audit:axe
echo   npm run lh:mobile
echo   npm run lh:desktop
echo Done.
goto :eof

:err
echo Audit failed. See errors above.
exit /b 1
endlocal

