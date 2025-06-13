import tornado


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header(
            "Access-Control-Allow-Methods",
            "GET, POST, PUT, DELETE, OPTIONS"
        )
        self.set_header("Content-Type", "application/json")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    def write_error(self, status_code, **kwargs):
        self.set_header("Content-Type", "application/json")
        error_message = "An error occurred"

        if "exc_info" in kwargs:
            error_message = str(kwargs["exc_info"][1])

        self.write({
            "error": error_message,
            "status_code": status_code
        })
