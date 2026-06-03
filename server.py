import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8001

class ServerHandler(BaseHTTPRequestHandler):  
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = f"Hello from the server! You requested: {PORT}\n"
        self.wfile.write(message.encode ('utf-8'))

    def log_message(self, format, *args):
        print(f"[server:{PORT}] {self.command} {self.path}")

if __name__ == "__main__":
    server = HTTPServer(("", PORT), ServerHandler)
    print(f"Server running on http://localhost:{PORT} (Ctrl+C to stop)")
    server.serve_forever()