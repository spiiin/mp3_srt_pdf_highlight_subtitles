import os
import re
import http.server
import socketserver

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        if not os.path.exists(path):
            self.send_error(404, "File not found")
            return None

        file_size = os.path.getsize(path)
        range_header = self.headers.get('Range')

        if range_header:
            range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
            if range_match:
                start = int(range_match.group(1))
                end = range_match.group(2)
                end = int(end) if end else file_size - 1

                if start >= file_size:
                    self.send_error(416, "Requested Range Not Satisfiable")
                    return None

                self.send_response(206)
                self.send_header('Content-type', self.guess_type(path))
                self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Content-Length', end - start + 1)
                self.end_headers()

                return open(path, 'rb'), start, end
        self.send_response(200)
        self.send_header('Content-type', self.guess_type(path))
        self.send_header('Content-Length', file_size)
        self.end_headers()

        return open(path, 'rb')

    def do_GET(self):
        if self.path.endswith(".mp3"):
            try:
                result = self.send_head()
                if isinstance(result, tuple):
                    f, start, end = result
                    if f:
                        with f:
                            f.seek(start)
                            self.wfile.write(f.read(end - start + 1))
                elif result:
                    with result as f:
                        self.copyfile(f, self.wfile)
            except Exception as e:
                self.send_error(500, f"Server error: {e}")
        else:
            super().do_GET()

PORT = 8000
ADDRESS = "0.0.0.0"
with socketserver.TCPServer((ADDRESS, PORT), CustomHandler) as httpd:
    print(f"Server started at {PORT}")
    httpd.serve_forever()
