import sys
import os
import webbrowser
import threading
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def open_browser():
    time.sleep(1.5)
    print("\n[+] Opening browser at http://127.0.0.1:8002 ...")
    webbrowser.open("http://127.0.0.1:8002")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

    print("=" * 65)
    print("[*] Launching Contract Risk Intelligence & Redlining Platform")
    print("=" * 65)

    threading.Thread(target=open_browser, daemon=True).start()

    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8002, reload=True)
