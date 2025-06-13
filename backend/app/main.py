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
    UserHandler,
    ActiveReservationsHandler
)
from db.cassandra import init_cassandra, close_cassandra

PORT = int(os.environ.get("PORT", 8000))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def make_app() -> tornado.web.Application:
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
        (r"/api/users/([^/]+)/active-reservations", ActiveReservationsHandler),

    ], debug=True)


async def main():
    try:
        await init_cassandra()

        app = make_app()
        app.listen(PORT)
        print(f"Server started at http://localhost:{PORT}")
        print("\n📚 Library Management System API Endpoints:")
        print("=" * 60)

        print("\n🔖 RESERVATION ENDPOINTS:")
        print("  POST   /api/reservations - Make a reservation")
        print("  PUT    /api/reservations/{id} - Update reservation")
        print("  GET    /api/reservations/{id} - Get specific reservation")
        print(
            "  GET    /api/reservations/user/{user_id} - "
            "Get user's ALL reservations"
        )
        print(
            "  GET    /api/reservations/book/{book_id} - "
            "Get book's ALL reservations"
        )
        print("  DELETE /api/reservations/bulk - Cancel multiple reservations")

        print("\n📖 BOOK ENDPOINTS:")
        print(
            "  GET    /api/books - List all books "
            "(?available=true for available only)"
        )
        print("  GET    /api/books/{book_id} - Get specific book")
        print("  POST   /api/books - Create book")
        print(
            "  GET    /api/books/{book_id}/availability - "
            "Check book availability (fast)"
        )

        print("\n👤 USER ENDPOINTS:")
        print("  GET    /api/users - List all users")
        print("  GET    /api/users/{user_id} - Get user info")
        print("  POST   /api/users - Create user")
        print(
            "  GET    /api/users/{user_id}/active-reservations - "
            "Get ACTIVE reservations (fast)"
        )

        print("\n🚀 NEW FAST ENDPOINTS:")
        print(
            "  GET    /api/users/{user_id}/active-reservations - "
            "O(1) active reservations lookup"
        )
        print(
            "  GET    /api/books/{book_id}/availability - "
            "O(1) availability check"
        )

        print("=" * 60)
        print(
            "✅ All tables use proper partition keys - "
            "NO ALLOW FILTERING warnings!"
        )
        print("✅ Active reservations stored separately for fast lookups")
        print("✅ Complete reservation history preserved")

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
        except Exception:
            pass
        print("Server stopped.")
