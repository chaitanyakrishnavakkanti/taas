#!/usr/bin/env python3
"""
Deep Researcher Agent - Streamlit App Launcher
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit app."""
    print("🚀 Starting Deep Researcher Agent...")
    print("📱 Opening web interface...")
    print("🌐 The app will open in your default browser")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Run streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Deep Researcher Agent stopped.")
    except Exception as e:
        print(f"❌ Error starting the app: {e}")
        print("💡 Make sure you have installed all requirements: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
