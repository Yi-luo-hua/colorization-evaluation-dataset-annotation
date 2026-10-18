"""Temporarily serve the authorized review JSON on loopback for Label Studio import."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

EXPORT = Path(__file__).resolve().parents[1] / 'runtime/pilot_384_20261015_01/exports/tasks_NR_pilot_partial_48_stream.json'


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/tasks_NR_pilot_partial_48_stream.json':
            self.send_error(404)
            return
        payload = EXPORT.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == '__main__':
    HTTPServer(('127.0.0.1', 8766), Handler).serve_forever()
