@echo off
cd /d "%~dp0backend"
if not exist ume_final.db (
    echo Seeding DB...
    python seed.py
)
echo Server starting: http://localhost:5000
python server.py
pause