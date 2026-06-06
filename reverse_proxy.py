from http.server import BaseHTTPRequestHandler, HTTPServer
import requests

LISTEN_PORT = 9000

BACKEND = "http://localhost:8001"

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            backend_response = requests.get(BACKEND + self.path, timeout=5)
        except requests.exceptions.RequestException as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(f"Bad Gateway: backend unreachable ({e})\n".encode('utf-8'))
            return
        
        self.send_response(backend_response.status_code)
        self.send_header('Content-type', backend_response.headers.get("Content-Type", "text/plain"))
        self.end_headers()
        self.wfile.write(backend_response.content)

    def log_message(self,format,*args):
        print(f"[proxy:{LISTEN_PORT}] {self.command} {self.path} -> {BACKEND}")

if __name__ == "__main__":
    server = HTTPServer(("", LISTEN_PORT), ProxyHandler)
    print(f"Reverse proxy running on http://localhost:{LISTEN_PORT} -> {BACKEND} (Ctrl+C to stop)")
    server.serve_forever()

