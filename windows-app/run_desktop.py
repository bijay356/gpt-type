# run_desktop.py - Standalone Python Desktop Runner
import os
import sys
import subprocess
import webbrowser

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(CURRENT_DIR, "index.html")

def launch_desktop():
    # 1. Try launching Edge in dedicated app window mode (zero browser clutter)
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    for ep in edge_paths:
        if os.path.exists(ep):
            cmd = [ep, f'--app=file:///{INDEX_PATH.replace(os.sep, "/")}', '--window-size=1320,860']
            subprocess.Popen(cmd)
            print("Launched GPT-TYPE Desktop via Edge Application Engine!")
            return

    # 2. Fallback to default browser
    webbrowser.open(f'file:///{INDEX_PATH.replace(os.sep, "/")}')
    print("Launched GPT-TYPE in default web browser.")

if __name__ == "__main__":
    launch_desktop()
