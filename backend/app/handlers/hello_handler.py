import tornado.web

class HelloHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def get(self):
        self.write({"message": "Hello, world!"})
