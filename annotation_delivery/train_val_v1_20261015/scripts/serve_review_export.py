"""Serve exactly one exported JSON on loopback for the local Label Studio import UI."""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('export',type=Path)
args = parser.parse_args()
payload = args.export.read_bytes()
route = '/' + args.export.name


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != route:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


HTTPServer(('127.0.0.1',8766),Handler).serve_forever()
