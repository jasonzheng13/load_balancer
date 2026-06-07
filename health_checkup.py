from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import threading
import time

LISTEN_PORT = 9000

ALL_BACKENDS = ["http://localhost:8001", "http://localhost:8002", "http://localhost:8003"]

HEALTH_CHECK_INTERVALS = 3

healthy_backends = list(ALL_BACKENDS)
next_index = 0
lock = threading.Lock()

def health_check_loop():
    global healthy_backends
    while True:
        currently_healthy = []
        for backend in ALL_BACKENDS:
            try:
                r = requests.get(backend + "/", timeout = 2)
                if r.status_code == 200:
                    currently_healthy.append(backend)
            except requests.exceptions.RequestException:
                pass
        with lock:
            added = set(currently_healthy) - set(healthy_backends)
            removed = set(healthy_backends) - set(currently_healthy)
            healthy_backends = currently_healthy
            for b in added:
                print(f"[health] {b} is now healthy - added to rotation")
            for b in removed:
                print(f"[health] {b} is now unhealthy - removed from rotation")
        time.sleep(HEALTH_CHECK_INTERVALS)

def pick_backend():
    global next_index
    with lock:
        if not healthy_backends:
            return None
        backend = healthy_backends[next_index % len(healthy_backends)]
        next_index = (next_index + 1) % len(healthy_backends)
    return backend

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        backend = pick_backend()
        if backend is None:
            self.send_response(503)
            self.end_headers()
            self.wfile.write("Service Unavailable: no healthy backends\n".encode('utf-8'))
            return
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
        print(f"[health_checkup:{LISTEN_PORT}] {self.command} {self.path}")
    
if __name__ == "__main__":
    checker = threading.Thread(target=health_check_loop, daemon=True)
    checker.start()
    server = HTTPServer(("", LISTEN_PORT), ProxyHandler)
    print(f"Health-checking round-robin LB running on http://localhost:{LISTEN_PORT}")
    print(f"Monitoring backends: {ALL_BACKENDS}")
    server.serve_forever()




