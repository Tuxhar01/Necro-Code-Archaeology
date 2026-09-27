#!/usr/bin/env python3
"""
Simple HTTP server for Necro dashboard.
"""

import http.server
import socketserver
import webbrowser
from pathlib import Path
import sys
import json
import io
import traceback

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from necro.config import config
from necro.upload_handler import UploadHandler, UploadRejected, parse_multipart_data
from necro.repo_inspector import RepoInspector


import os

PORT = int(os.environ.get("PORT", 8000))
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

    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/api/analyze-upload':
            self._handle_analyze_upload()
        else:
            # Return 404 for unrelated POST endpoints
            self.send_error(404, "Not Found")

    def _handle_analyze_upload(self):
        """Handle repository upload and analysis."""
        extract_dir = None

        try:
            # Check Content-Length
            content_length = int(self.headers.get('Content-Length', 0))

            if content_length > UploadHandler.MAX_UPLOAD_SIZE:
                self.send_error(413, "Request Entity Too Large")
                return

            if content_length == 0:
                self.send_error(400, "No data received")
                return

            # Read request body
            body = self.rfile.read(content_length)

            # Parse multipart data
            content_type = self.headers.get('Content-Type', '')
            zip_data, filename = parse_multipart_data(content_type, body)

            if not zip_data:
                self.send_error(400, "No ZIP file found in upload")
                return

            # Validate it's a ZIP file
            if not filename or not filename.lower().endswith('.zip'):
                self.send_error(400, "Only ZIP files are accepted")
                return

            print(f"[Server] Received upload: {filename} ({len(zip_data)} bytes)")

            # Extract ZIP safely
            try:
                extract_dir = UploadHandler.safe_extract_zip(zip_data)
                print(f"[Server] Extracted to: {extract_dir}")
            except UploadRejected as e:
                self.send_error(400, str(e))
                return

            # Find analysis root
            analysis_root = UploadHandler.find_analysis_root(extract_dir)
            print(f"[Server] Analysis root: {analysis_root}")

            # Run static analysis
            inspector = RepoInspector(analysis_root)
            analysis_result = inspector.analyze()

            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            response_json = json.dumps(analysis_result, indent=2)
            self.wfile.write(response_json.encode('utf-8'))

            print(f"[Server] Analysis complete: {analysis_result['summary']['modules_analyzed']} modules")

        except UploadRejected as e:
            self.send_error(400, str(e))
        except Exception as e:
            print(f"[Server] Error during analysis: {e}")
            traceback.print_exc()
            self.send_error(500, "Internal server error")
        finally:
            # Clean up extracted files
            if extract_dir and extract_dir.exists():
                try:
                    UploadHandler.cleanup(extract_dir)
                    print(f"[Server] Cleaned up: {extract_dir}")
                except Exception as e:
                    print(f"[Server] Cleanup error: {e}")


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
