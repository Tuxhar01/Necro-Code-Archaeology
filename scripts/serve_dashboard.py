#!/usr/bin/env python3
"""
Simple HTTP server for Necro dashboard.
"""

import http.server
import socketserver
import webbrowser
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from necro.config import config


PORT = 8000
PROJECT_ROOT = config.PROJECT_ROOT


class NecroHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve from project root with dashboard as default."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)
    
    def translate_path(self, path):
        """Translate URL path to filesystem path, defaulting to dashboard for root."""
        # If requesting root, serve dashboard/index.html
        if path == '/':
            path = '/dashboard/index.html'
        elif not path.startswith('/results') and not path.startswith('/artifacts') and not path.startswith('/dashboard'):
            # Default other paths to dashboard directory
            path = '/dashboard' + path
        return super().translate_path(path)
    
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()


def main():
    """Start the dashboard server."""
    
    # Check if results exist
    results_file = config.RESULTS_DIR / "results.json"
    results_file_absolute = results_file.resolve()
    
    if not results_file.exists():
        print("⚠️  Warning: results.json not found!")
        print(f"   Expected at: {results_file_absolute}")
        print("   Run 'python scripts/run_pipeline.py' first to generate results.")
        print()
    
    # Start server
    with socketserver.TCPServer(("", PORT), NecroHTTPRequestHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"""
================================================================

   NECRO Dashboard Server

================================================================

Server running at: {url}
Serving from: {PROJECT_ROOT}
Results JSON at: {results_file_absolute}

Press Ctrl+C to stop the server
        """)
        
        # Open browser
        try:
            webbrowser.open(url)
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")


if __name__ == "__main__":
    main()

# Made with Bob
