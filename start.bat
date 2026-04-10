@echo off
cls
echo UttarakhandMockExams v3 - Light Theme
echo No Login Required / AdSense Ready
echo.
cd /d "%~dp0backend"
if not exist uttarakhandmockexams.db (
    echo Seeding 7200 questions...
    python seed.py
)
echo Server: http://localhost:5000
echo Admin: admin@uttarakhandmockexams.in / admin123
echo.
python server.py
pause
