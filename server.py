from http.server import SimpleHTTPRequestHandler
from http.server import HTTPServer
from urllib import parse
import berry
import json
import spotlock
import gpsmodule
class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if(self.path == "/location"):
            #todo, actually find a location
            message = json.dumps(gpsmodule.getLocation())
            self.send_response(200)
            self.send_header('Content-Type',
                    'text/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(message.encode("utf-8"))
        elif(self.path == "/spotlock"):
            message = spotlock.getSpotlockData()
            self.send_response(200)
            self.send_header('Content-Type',
                    'text/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(message.encode("utf-8"))
        else:
            self.path = "/public" + self.path
            self.send_response(200)
            self.send_header("Cache-Control","no-cache, no-store, must-revalidate")
            self.send_header("Pragma","no-cache")
            self.send_header("Expires","0")
            super().do_GET()
    def do_POST(self):
        if(self.path == "/spotlock"):
            data = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(data)
            spotlock.controlSpotLock(data["on"])
            self.send_response(200)
            self.end_headers()
            self.wfile.write(spotlock.getSpotlockData().encode("utf-8"))
if __name__ == '__main__':
    berry.start()
    spotlock.start()
    gpsmodule.start()
    server = HTTPServer(('localhost', 8888), Handler)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()
