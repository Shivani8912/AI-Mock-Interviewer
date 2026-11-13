"""
AI Mock Interviewer - Application Runner
Provides a clean, direct entry point for VS Code, terminal, and IDE execution.
"""

import os
import sys

# Suppress telemetry and credential prompts
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
cred_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".streamlit", "credentials.toml")
os.environ["STREAMLIT_CREDENTIALS_FILE_PATH"] = cred_path

from streamlit.web import cli as stcli

if __name__ == "__main__":
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
    print("\n" + "=" * 60)
    print("🎤  AI MOCK INTERVIEWER")
    print("=" * 60)
    print("🚀 Launching Streamlit web application...")
    print("📍 Local URL: http://localhost:8501")
    print("💡 Your browser should open automatically.")
    print("   If it does not, click or copy: http://localhost:8501")
    print("=" * 60 + "\n")

    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.headless=false",
        "--server.port=8501"
    ]
    sys.exit(stcli.main())
