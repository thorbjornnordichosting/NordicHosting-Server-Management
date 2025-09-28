#!/usr/bin/env python3
"""
Server för 10.0.0.38 - SSH och webbtjänst
"""

import http.server
import socketserver
import sys
import os
import subprocess

IP = "10.0.0.38"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

class ServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Server 10.0.0.38</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; }}
                .info {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .status {{ color: #28a745; font-weight: bold; }}
                .ssh-info {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🖥️ Server 10.0.0.38</h1>
                <div class="info">
                    <p><strong>IP-adress:</strong> {IP}</p>
                    <p><strong>Port:</strong> {PORT}</p>
                    <p><strong>Status:</strong> <span class="status">🟢 Online</span></p>
                    <p><strong>Server:</strong> Python HTTP Server</p>
                </div>
                <div class="ssh-info">
                    <h3>🔐 SSH-anslutning</h3>
                    <p><strong>SSH-kommando:</strong> <code>ssh root@{IP}</code></p>
                    <p><strong>Port:</strong> 22 (standard)</p>
                    <p><strong>Status:</strong> Kontrollera SSH-tjänst på servern</p>
                </div>
                <p>Denna server körs via Server Manager och är tillgänglig från nätverket!</p>
                <p><em>Startad: {os.popen('date').read().strip()}</em></p>
            </div>
        </body>
        </html>
        '''
        self.wfile.write(html_content.encode('utf-8'))

if __name__ == "__main__":
    with socketserver.TCPServer((IP, PORT), ServerHandler) as httpd:
        print(f"🌐 Server 10.0.0.38 startad på {IP}:{PORT}")
        print(f"   Tillgänglig via: http://{IP}:{PORT}")
        print(f"   SSH: ssh root@{IP}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Server 10.0.0.38 stoppad på {IP}:{PORT}")
