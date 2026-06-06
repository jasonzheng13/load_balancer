from http.server import BaseHTTPRequestHandler, HTTPServer
import requests 
import threading

LISTEN_PORT = 9000

BACKENDS = ["http://localhost:8001", "http://localhost:8002", "http://localhost:8003"]

_next_index = 0
_lock = threading.Lock()

def pick_backend():
    global _next_index
    with _lock:
        backend = BACKENDS[_next_index]
        _next_index = (_next_index + 1) % len(BACKENDS)
    return backend

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        backend = pick_backend()
        try:
            backend_response = requests.get(backend + self.path, timeout=5)
        except requests.exceptions.RequestException as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(f"Bad Gateway: {backend} unreachable ({e})\n".encode('utf-8'))
            return
        
        self.send_response(backend_response.status_code)
        self.send_header('Content-type', backend_response.headers.get("Content-Type", "text/plain"))
        self.end_headers()
        self.wfile.write(backend_response.content)
    
    def log_message(self,format,*args):
        print(f"[proxy:{LISTEN_PORT}] {self.command} {self.path} -> {pick_backend()}")

if __name__ == "__main__":
    server = HTTPServer(("", LISTEN_PORT), ProxyHandler)
    print(f"Round-robin proxy running on http://localhost:{LISTEN_PORT}")
    print(f"Balancing across: {BACKENDS}")
    server.serve_forever()