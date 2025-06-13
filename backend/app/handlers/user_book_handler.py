import tornado.web
import json
import uuid
from datetime import datetime
from db.cassandra import execute_async  # type: ignore
import logging

logger = logging.getLogger(__name__)


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header(
            "Access-Control-Allow-Methods",
            "GET, POST, PUT, DELETE, OPTIONS"
        )
        self.set_header("Content-Type", "application/json")

    def options(self):
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


class UserReservationsHandler(BaseHandler):
    async def get(self, user_id):
        """Get all reservations for a user (active + completed)"""
        try:
            user_uuid = uuid.UUID(user_id)

            # Get reservations from reservations_by_user table
            query = """
                SELECT reservation_id, book_id, book_title, status,
                       reservation_date, return_deadline
                FROM reservations_by_user
                WHERE user_id = %s
            """
            result = await execute_async(query, (user_uuid,))

            reservations = []
            for row in result:
                reservations.append({
                    "reservation_id": str(row.reservation_id),
                    "book_id": str(row.book_id),
                    "book_title": row.book_title,
                    "status": row.status,
                    "reservation_date": row.reservation_date.isoformat(),
                    "return_deadline": row.return_deadline.isoformat()
                })

            self.write({
                "user_id": str(user_uuid),
                "reservations": reservations,
                "total_count": len(reservations)
            })

        except ValueError:
            self.set_status(405)
            self.write({"error": "Invalid user ID format"})
        except Exception as e:
            logger.error(f"Error fetching user reservations: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})


class BookReservationsHandler(BaseHandler):
    async def get(self, book_id):
        """Get all reservations for a book (active + completed)"""
        try:
            book_uuid = uuid.UUID(book_id)

            # Get reservations from reservations_by_book table
            query = """
                SELECT reservation_id, user_id, user_name, status,
                       reservation_date, return_deadline
                FROM reservations_by_book
                WHERE book_id = %s
            """
            result = await execute_async(query, (book_uuid,))

            reservations = []
            for row in result:
                reservations.append({
                    "reservation_id": str(row.reservation_id),
                    "user_id": str(row.user_id),
                    "user_name": row.user_name,
                    "status": row.status,
                    "reservation_date": row.reservation_date.isoformat(),
                    "return_deadline": row.return_deadline.isoformat()
                })

            self.write({
                "book_id": str(book_uuid),
                "reservations": reservations,
                "total_count": len(reservations)
            })

        except ValueError:
            self.set_status(406)
            self.write({"error": "Invalid book ID format"})
        except Exception as e:
            logger.error(f"Error fetching book reservations: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})


class BookHandler(BaseHandler):
    async def get(self, book_id=None):
        """Get a specific book or list all books"""
        try:
            if book_id:
                # Get specific book
                book_uuid = uuid.UUID(book_id)
                query = "SELECT * FROM books WHERE book_id = %s"
                result = await execute_async(query, (book_uuid,))

                if not result:
                    self.set_status(404)
                    self.write({"error": "Book not found"})
                    return

                book = result[0]
                self.write({
                    "book_id": str(book.book_id),
                    "title": book.title,
                    "status": book.status,
                    "created_at": book.created_at.isoformat()
                })
            else:
                # List all books, optionally filter by availability
                available_arg = self.get_argument("available", "false")
                available_only = available_arg.lower() == "true"

                if available_only:
                    query = (
                        "SELECT * FROM books WHERE status = 'available' "
                        "ALLOW FILTERING"
                    )
                    result = await execute_async(query)
                else:
                    query = "SELECT * FROM books"
                    result = await execute_async(query)

                books = []
                for book in result:
                    books.append({
                        "book_id": str(book.book_id),
                        "title": book.title,
                        "status": book.status,
                        "created_at": book.created_at.isoformat()
                    })

                self.write({
                    "books": books,
                    "total_count": len(books),
                    "filter_applied": (
                        "available_only" if available_only else "none"
                    )
                })

        except ValueError:
            self.set_status(407)
            self.write({"error": "Invalid book ID format"})
        except Exception as e:
            logger.error(f"Error fetching books: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})

    async def post(self):
        """Create a new book"""
        try:
            data = json.loads(self.request.body)

            # Validate required fields
            if 'title' not in data:
                self.set_status(408)
                self.write({"error": "Missing required field: title"})
                return

            book_id = uuid.uuid4()
            now = datetime.utcnow()

            # Insert book
            query = """
                INSERT INTO books (book_id, title, status, created_at)
                VALUES (%s, %s, %s, %s)
            """
            await execute_async(
                query,
                (book_id, data['title'], 'available', now)
            )

            self.set_status(201)
            self.write({
                "book_id": str(book_id),
                "title": data['title'],
                "status": "available",
                "created_at": now.isoformat()
            })

        except json.JSONDecodeError:
            self.set_status(409)
            self.write({"error": "Invalid JSON"})
        except Exception as e:
            logger.error(f"Error creating book: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})


class BookAvailabilityHandler(BaseHandler):
    async def get(self, book_id):
        """
        Check if a book is available (fast O(1) lookup using book status)
        """
        try:
            book_uuid = uuid.UUID(book_id)

            # Check book status directly - this is O(1) and efficient
            book_query = "SELECT book_id, title, status FROM books WHERE book_id = %s"
            book_result = await execute_async(book_query, (book_uuid,))
            if not book_result:
                self.set_status(404)
                self.write({"error": "Book not found"})
                return

            book = book_result[0]
            is_available = book.status == 'available'

            self.write({
                "book_id": str(book_uuid),
                "title": book.title,
                "available": is_available,
                "status": book.status
            })

        except ValueError:
            self.set_status(410)
            self.write({"error": "Invalid book ID format"})
        except Exception as e:
            logger.error(f"Error checking book availability: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})


class ActiveReservationsHandler(BaseHandler):
    async def get(self, user_id):
        """
        Get active reservations for a user
        (fast O(1) lookup using reservations_user_book)
        """
        try:
            user_uuid = uuid.UUID(user_id)

            # Check if user exists
            user_query = "SELECT username FROM users WHERE user_id = %s"
            user_result = await execute_async(user_query, (user_uuid,))
            if not user_result:
                self.set_status(404)
                self.write({"error": "User not found"})
                return

            # Get active reservations from reservations_user_book table
            query = """
                SELECT book_id, reservation_id, book_title, reservation_date,
                       return_deadline, created_at
                FROM reservations_user_book
                WHERE user_id = %s
            """
            result = await execute_async(query, (user_uuid,))

            active_reservations = []
            for row in result:
                active_reservations.append({
                    "reservation_id": str(row.reservation_id),
                    "book_id": str(row.book_id),
                    "book_title": row.book_title,
                    "reservation_date": row.reservation_date.isoformat(),
                    "return_deadline": row.return_deadline.isoformat(),
                    "created_at": row.created_at.isoformat()
                })

            self.write({
                "user_id": str(user_uuid),
                "username": user_result[0].username,
                "active_reservations": active_reservations,
                "active_count": len(active_reservations)
            })

        except ValueError:
            self.set_status(411)
            self.write({"error": "Invalid user ID format"})
        except Exception as e:
            logger.error(f"Error fetching active reservations: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})


class UserHandler(BaseHandler):
    async def get(self, user_id=None):
        """Get a specific user or list all users"""
        try:
            if user_id:
                # Get specific user
                user_uuid = uuid.UUID(user_id)
                query = "SELECT * FROM users WHERE user_id = %s"
                result = await execute_async(query, (user_uuid,))

                if not result:
                    self.set_status(404)
                    self.write({"error": "User not found"})
                    return

                user = result[0]

                # Also get active reservations count for this user
                active_query = (
                    "SELECT COUNT(*) FROM reservations_user_book "
                    "WHERE user_id = %s"
                )
                active_result = await execute_async(active_query, (user_uuid,))
                active_count = active_result[0].count if active_result else 0

                self.write({
                    "user_id": str(user.user_id),
                    "username": user.username,
                    "created_at": user.created_at.isoformat(),
                    "active_reservations_count": active_count
                })
            else:
                # List all users
                query = "SELECT * FROM users"
                result = await execute_async(query)

                users = []
                for user in result:
                    users.append({
                        "user_id": str(user.user_id),
                        "username": user.username,
                        "created_at": user.created_at.isoformat()
                    })

                self.write({
                    "users": users,
                    "total_count": len(users)
                })

        except ValueError:
            self.set_status(412)
            self.write({"error": "Invalid user ID format"})
        except Exception as e:
            logger.error(f"Error fetching users: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})

    async def post(self):
        """Create a new user"""
        try:
            data = json.loads(self.request.body)

            # Validate required fields
            if 'username' not in data:
                self.set_status(413)
                self.write({"error": "Missing required field: username"})
                return

            user_id = uuid.uuid4()
            now = datetime.utcnow()

            # Insert user
            query = """
                INSERT INTO users (user_id, username, created_at)
                VALUES (%s, %s, %s)
            """
            await execute_async(query, (user_id, data['username'], now))

            self.set_status(201)
            self.write({
                "user_id": str(user_id),
                "username": data['username'],
                "created_at": now.isoformat()
            })

        except json.JSONDecodeError:
            self.set_status(414)
            self.write({"error": "Invalid JSON"})
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})
