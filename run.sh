#!/bin/bash
# Convenient runner for AI Mock Interviewer
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "============================================================"
echo "🎤  AI MOCK INTERVIEWER"
echo "============================================================"
echo "🚀 Launching application at http://localhost:8501 ..."
echo "============================================================"

if [ -f "venv/bin/streamlit" ]; then
    ./venv/bin/streamlit run app.py --server.headless=false --server.port=8501
else
    python3 -m streamlit run app.py --server.headless=false --server.port=8501
fi
