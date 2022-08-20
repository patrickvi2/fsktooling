from http.server import BaseHTTPRequestHandler, HTTPServer


class OdfRequestHandler(BaseHTTPRequestHandler):
    def set_header(self):
        self.send_response(200)
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-HOVTP-Environment", self.headers["X-HOVTP-Environment"])
        self.send_header("X-HOVTP-Last-Serial-Number", self.headers["X-HOVTP-Last-Serial-Number"])
        self.end_headers()

    def do_OPTIONS(self):
        self.set_header()

    def do_POST(self):
        self.set_header()
        print(self.headers)
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        if content_length > 0:
            print(post_data)


def main():
    host_name = "localhost"
    server_port = 11111
    web_server = HTTPServer((host_name, server_port), OdfRequestHandler)
    print("Server started http://%s:%s" % (host_name, server_port))

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass

    web_server.server_close()
    print("Server stopped.")


if __name__ == "__main__":
    main()