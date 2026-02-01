#!/usr/bin/env python3
"""
Simple HTTP server for MediCare AI frontend
"""
import http.server
import socketserver
import os
from urllib.parse import unquote

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with CORS support"""

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        super().end_headers()

    def do_GET(self):
        # Serve index.html for root path
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        # Decode URL
        self.path = unquote(self.path)
        return super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    PORT = 8080
    os.chdir('/home/houge/Dev/MediCare_AI/frontend')
    
    with socketserver.TCPServer(("0.0.0.0", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"MediCare AI Frontend Server running at http://0.0.0.0:{PORT}")
        print(f"Access from LAN: http://192.168.50.115:{PORT}")
        httpd.serve_forever()
