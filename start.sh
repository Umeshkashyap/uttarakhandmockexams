#!/bin/bash
clear
echo "╔══════════════════════════════════════════════════════╗"
echo "║       UttarakhandMockExams — Starting...             ║"
echo "║    Uttarakhand Daily Mock Exam Portal                ║"
echo "║    SSC · RRB · Bank · UKSSC · UKPSC                 ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
cd "$(dirname "$0")/backend"
if [ ! -f uttarakhandmockexams.db ]; then
    echo "  Seeding 7,200 questions for first run..."
    python3 seed.py
    echo ""
fi
echo "  Server starting at http://localhost:5000"
echo "  Admin: admin@uttarakhandmockexams.in / admin123"
echo "  Student: demo@uttarakhandmockexams.in / demo123"
echo ""
python3 server.py
