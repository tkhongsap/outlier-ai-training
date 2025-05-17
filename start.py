import os
import subprocess
import threading
import time
import webbrowser

def start_flask():
    """Start the Flask backend server"""
    print("Starting Flask backend server...")
    subprocess.Popen(['python', 'app.py'])

def start_http_server():
    """Start a simple HTTP server for the frontend"""
    print("Starting HTTP server for frontend...")
    # Use Python's built-in HTTP server
    subprocess.Popen(['python', '-m', 'http.server', '8000'])

def main():
    # Start both servers in separate threads
    backend_thread = threading.Thread(target=start_flask)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Give the Flask server a moment to start
    time.sleep(2)
    
    # Start the frontend HTTP server
    frontend_thread = threading.Thread(target=start_http_server)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    print("\n=== Profile App Started ===")
    print("Backend API: http://localhost:5000/api")
    print("Frontend: http://localhost:8000")
    print("\nOpen your browser to http://localhost:8000 to view the app")
    print("Press Ctrl+C to stop all servers\n")
    
    # Open the browser to the frontend
    webbrowser.open('http://localhost:8000')
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")

if __name__ == "__main__":
    main() 