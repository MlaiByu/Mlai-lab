#!/usr/bin/env python3
import http.server
import socketserver
import pickle
import base64
import os

FLAG = "Mlai{python_pickle_flag}"

class FlagReader:
    def __reduce__(self):
        return (os.system, ('cat /flag.txt',))

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Testing page')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        params = dict(x.split('=') for x in post_data.decode().split('&'))
        data = params.get('data', '')

        if data:
            try:
                decoded = base64.b64decode(data)
                obj = pickle.loads(decoded)
                result = str(obj)
            except Exception as e:
                result = str(e)
        else:
            result = ""

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(result.encode())

if __name__ == "__main__":
    PORT = 8000
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Server running on port {PORT}")
        httpd.serve_forever()