#!/usr/bin/env python3
"""
SVT Dashboard Launcher
Startet das Therapeuten-Dashboard mit eingebautem HTTP-Server

Usage:
    python dashboard_server.py [--port 8080]
"""

import http.server
import socketserver
import argparse
import os
import webbrowser
import threading
import signal
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for the dashboard"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[Dashboard] {args[0]}")

def start_server(port=PORT, open_browser=True):
    """Start the HTTP server"""
    
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
        print(f"\n🧠 SVT Therapeuten Dashboard")
        print(f"   URL: http://localhost:{port}")
        print(f"   Verzeichnis: {DIRECTORY}")
        print(f"\n   Drücke Ctrl+C zum Beenden\n")
        
        # Open browser in new thread
        if open_browser:
            threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{port}")).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard wird beendet...")
            sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SVT Dashboard Server")
    parser.add_argument("--port", type=int, default=PORT, help="Port für Server")
    parser.add_argument("--no-browser", action="store_true", help="Browser nicht automatisch öffnen")
    
    args = parser.parse_args()
    
    start_server(port=args.port, open_browser=not args.no-browser)
