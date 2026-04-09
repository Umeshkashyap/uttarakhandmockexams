@echo off
cls
echo  UttarakhandMockExams - Uttarakhand Daily Mock Exam Portal
echo  SSC . RRB . Bank . UKSSC . UKPSC
echo.
cd /d "%~dp0backend"
if not exist uttarakhandmockexams.db (
    echo  Seeding 7200 questions for first run...
    python seed.py
    echo.
)
echo  Server starting at http://localhost:5000
echo  Admin: admin@uttarakhandmockexams.in / admin123
echo  Student: demo@uttarakhandmockexams.in / demo123
echo.
python server.py
pause
