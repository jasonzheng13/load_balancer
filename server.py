import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8001

class ServerHandler(BaseHTTPRequestHandler):  
