import asyncio
import os
import tornado.web
import tornado.platform.asyncio

from handlers.hello_handler import HelloHandler
from db.cassandra import init_cassandra, close_cassandra

PORT = int(os.environ.get("PORT", 8000))


def make_app():
    return tornado.web.Application([
        (r"/api/hello", HelloHandler),
    ], debug=True)


async def main():
    await init_cassandra()

    app = make_app()
    app.listen(PORT)
    print(f"Server started at http://localhost:{PORT}")

    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        tornado.platform.asyncio.AsyncIOMainLoop().install()
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down gracefully...")
        asyncio.run(close_cassandra())
