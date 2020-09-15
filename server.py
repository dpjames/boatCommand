from http.server import SimpleHTTPRequestHandler
from http.server import HTTPServer
from urllib import parse
import berry
import json
import spotlock
import compass
import gpsmodule
import traceback
class Handler(SimpleHTTPRequestHandler):
    def send_json(self, msg):
       message = json.dumps(msg)
       self.send_response(200)
       self.send_header('Content-Type',
               'text/json; charset=utf-8')
       self.end_headers()
       self.wfile.write(message.encode("utf-8"))
    def log_message(self, format, *args):
        pass
    def do_GET(self):
        if(self.path == "/location"):
            self.send_json(gpsmodule.getLocation())
        elif(self.path == "/compass"):
            self.send_json(compass.getHeading())
        elif(self.path == "/spotlock"):
            self.send_json(spotlock.getSpotlockData())
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
            self.send_json(spotlock.getSpotlockData())
if __name__ == '__main__':
    try:
        if hasattr(berry, "start"):
            berry.start()
        if hasattr(spotlock, "start"):
            spotlock.start()
        if hasattr(gpsmodule, "start"):
            gpsmodule.start()
        server = HTTPServer(('192.168.1.13', 8000), Handler)
        print('Starting server, use <Ctrl-C> to stop')
        server.serve_forever()
    except Exception as e:
        print(e)
        traceback.print_exc()


