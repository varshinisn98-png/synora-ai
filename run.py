import os
import sys
import subprocess
import time

def run_services():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")
    
    # 1. Start Backend FastAPI
    print("Starting FastAPI Backend...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=backend_dir
    )
    
    # Give backend a moment to initialize
    time.sleep(2)
    
    # Check if backend crashed immediately
    if backend_process.poll() is not None:
        print("Backend failed to start.")
        sys.exit(1)
        
    print("FastAPI Backend started on http://127.0.0.1:8000")
    
    # 2. Start Frontend Streamlit
    print("Starting Streamlit Frontend...")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py"],
        cwd=frontend_dir
    )
    
    time.sleep(2)
    
    # Check if frontend crashed immediately
    if frontend_process.poll() is not None:
        print("Frontend failed to start.")
        backend_process.terminate()
        sys.exit(1)
        
    print("Streamlit Frontend started successfully!")
    print("\nPress Ctrl+C to stop both services.")
    
    try:
        while True:
            # Check if processes are still running
            backend_status = backend_process.poll()
            frontend_status = frontend_process.poll()
            
            if backend_status is not None:
                print(f"\nBackend exited with code {backend_status}")
                break
            if frontend_status is not None:
                print(f"\nFrontend exited with code {frontend_status}")
                break
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        # Terminate processes
        backend_process.terminate()
        frontend_process.terminate()
        
        # Wait for them to shut down
        backend_process.wait()
        frontend_process.wait()
        print("Services stopped.")

if __name__ == "__main__":
    run_services()
