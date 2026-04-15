#!/bin/bash
clear
echo "======================================"
echo "  UttarakhandMockExams"
echo "  Free Mock Test Portal"
echo "======================================"
cd "$(dirname "$0")"
if [ ! -f uttarakhandmockexams.db ] || [ $(python3 -c "import sqlite3;c=sqlite3.connect('uttarakhandmockexams.db');print(c.execute('SELECT COUNT(*) FROM subjects').fetchone()[0])" 2>/dev/null || echo 0) -lt 5 ]; then
    echo "  First run — seeding 23,400 questions..."
    python3 seed.py
fi
echo ""
echo "  ✅ Server: http://localhost:5000"
echo "  👤 Admin: admin@uttarakhandmockexams.in / admin123"
echo ""
python3 server.py
