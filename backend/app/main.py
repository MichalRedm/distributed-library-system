import asyncio
import os
import tornado.web
import tornado.platform.asyncio
import logging

from handlers.hello_handler import HelloHandler
from handlers.reservation_handler import (
    ReservationHandler, 
    ReservationDetailHandler, 
    BulkReservationHandler
)
from handlers.user_book_handler import (
    UserReservationsHandler,
    BookReservationsHandler,
    BookHandler,
    BookAvailabilityHandler,
    UserHandler
)
from db.cassandra import init_cassandra, close_cassandra

PORT = int(os.environ.get("PORT", 8000))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def make_app():
    return tornado.web.Application([
        # Original hello endpoint
        (r"/api/hello", HelloHandler),
        
        # Reservation endpoints
        (r"/api/reservations", ReservationHandler),
        (r"/api/reservations/bulk", BulkReservationHandler),
        (r"/api/reservations/([^/]+)", ReservationDetailHandler),
        (r"/api/reservations/user/([^/]+)", UserReservationsHandler),
        (r"/api/reservations/book/([^/]+)", BookReservationsHandler),
        
        # Book endpoints
        (r"/api/books", BookHandler),
        (r"/api/books/([^/]+)", BookHandler),
        (r"/api/books/([^/]+)/availability", BookAvailabilityHandler),
        
        # User endpoints
        (r"/api/users", UserHandler),
        (r"/api/users/([^/]+)", UserHandler),
        
    ], debug=True)


async def main():
    try:
        await init_cassandra()
        
        app = make_app()
        app.listen(PORT)
        print(f"Server started at http://localhost:{PORT}")
        print("Available endpoints:")
        print("  POST   /api/reservations - Make a reservation")
        print("  PUT    /api/reservations/{id} - Update reservation")
        print("  GET    /api/reservations/{id} - Get specific reservation")
        print("  GET    /api/reservations/user/{user_id} - Get user's reservations")
        print("  GET    /api/reservations/book/{book_id} - Get book's reservations")
        print("  DELETE /api/reservations/bulk - Cancel multiple reservations")
        print("  GET    /api/books - List all books (?available=true for available only)")
        print("  GET    /api/books/{book_id} - Get specific book")
        print("  POST   /api/books - Create book")
        print("  GET    /api/books/{book_id}/availability - Check book availability")
        print("  POST   /api/users - Create user")
        print("  GET    /api/users/{user_id} - Get user info")
        
        await asyncio.Event().wait()
        
    except Exception as e:
        logging.error(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    try:
        tornado.platform.asyncio.AsyncIOMainLoop().install()
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        try:
            asyncio.run(close_cassandra())
        except:
            pass
        print("Server stopped.")