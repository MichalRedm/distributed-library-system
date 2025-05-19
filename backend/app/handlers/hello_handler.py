import tornado.web

class HelloHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"message": "Hello, world!"})
