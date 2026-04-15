@echo off
cls
echo UttarakhandMockExams - Free Mock Test Portal
echo.
cd /d "%~dp0"
if not exist uttarakhandmockexams.db (
    echo First run - seeding questions...
    python seed.py
)
echo Server: http://localhost:5000
echo Admin: admin@uttarakhandmockexams.in / admin123
echo.
python server.py
pause
