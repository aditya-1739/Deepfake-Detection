import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def main():
    print("Starting Deepfake Detection System...")
    workspace = Path(__file__).resolve().parent
    
    # 1. Start Backend using its venv
    backend_venv = workspace / "backend/venv/Scripts/python.exe"
    backend_main = workspace / "backend/app/main.py"
    
    if not backend_venv.exists():
        print(f"Error: Backend virtual environment not found at {backend_venv}")
        sys.exit(1)
        
    print("-> Starting FastAPI Backend on http://127.0.0.1:8000")
    backend_process = subprocess.Popen(
        [str(backend_venv), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(workspace / "backend")
    )
    
    # Wait for backend to initialize
    time.sleep(3)
    
    # 2. Start Frontend Server
    print("-> Starting Frontend Server on http://127.0.0.1:3000")
    # We can just use the global python or backend venv to serve the frontend folder
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "3000"],
        cwd=str(workspace / "frontend")
    )
    
    print("\n[SUCCESS] System is running!")
    print("-> Access the UI at: http://127.0.0.1:3000")
    print("Press Ctrl+C to stop both servers.\n")
    
    def signal_handler(sig, frame):
        print("\nStopping servers...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("Servers stopped.")
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    
    # Keep main thread alive
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
