import tornado.web
import json
import uuid
from datetime import datetime
from db.cassandra import execute_async
import logging

logger = logging.getLogger(__name__)

class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
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
        """Get all reservations for a specific user"""
        try:
            user_uuid = uuid.UUID(user_id)
            
            query = "SELECT * FROM reservations_by_user WHERE user_id = ?"
            result = await execute_async(query, (user_uuid,))
            
            reservations = []
            for row in result:
                reservations.append({
                    "reservation_id": str(row.reservation_id),
                    "user_id": str(user_uuid),
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
            self.set_status(400)
            self.write({"error": "Invalid user ID format"})
        except Exception as e:
            logger.error(f"Error fetching user reservations: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})

class BookReservationsHandler(BaseHandler):
    async def get(self, book_id):
        """Get all reservations for a specific book"""
        try:
            book_uuid = uuid.UUID(book_id)
            
            query = "SELECT * FROM reservations_by_book WHERE book_id = ?"
            result = await execute_async(query, (book_uuid,))
            
            reservations = []
            for row in result:
                reservations.append({
                    "reservation_id": str(row.reservation_id),
                    "user_id": str(row.user_id),
                    "book_id": str(book_uuid),
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
            self.set_status(400)
            self.write({"error": "Invalid book ID format"})
        except Exception as e:
            logger.error(f"Error fetching book reservations: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})

class BookHandler(BaseHandler):
    async def get(self, book_id=None):
        """Get all books or a specific book"""
        try:
            if book_id:
                # Get specific book
                book_uuid = uuid.UUID(book_id)
                query = "SELECT * FROM books WHERE book_id = ?"
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
                # Get all books
                available_only = self.get_argument("available", None)
                
                if available_only and available_only.lower() == "true":
                    # Note: This is not efficient for large datasets in Cassandra
                    # In production, consider using a separate table for available books
                    query = "SELECT * FROM books WHERE status = 'available' ALLOW FILTERING"
                else:
                    query = "SELECT * FROM books"
                
                result = await execute_async(query)
                
                books = []
                for row in result:
                    books.append({
                        "book_id": str(row.book_id),
                        "title": row.title,
                        "status": row.status,
                        "created_at": row.created_at.isoformat()
                    })
                
                self.write({
                    "books": books,
                    "total_count": len(books)
                })
                
        except ValueError:
            self.set_status(400)
            self.write({"error": "Invalid book ID format"})
        except Exception as e:
            logger.error(f"Error fetching books: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})

    async def post(self):
        """Create a new book"""
        try:
            data = json.loads(self.request.body)
            
            if 'title' not in data:
                self.set_status(400)
                self.write({"error": "Missing required field: title"})
                return
            
            book_id = uuid.uuid4()
            now = datetime.utcnow()
            
            query = """
                INSERT INTO books (book_id, title, status, created_at)
                VALUES (?, ?, ?, ?)
            """
            
            await execute_async(query, (book_id, data['title'], 'available', now))
            
            self.set_status(201)
            self.write({
                "book_id": str(book_id),
                "title": data['title'],
                "status": "available",
                "created_at": now.isoformat()
            })
            
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"error": "Invalid JSON"})
        except Exception as e:
            logger.error(f"Error creating book: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})

class BookAvailabilityHandler(BaseHandler):
    async def get(self, book_id):
        """Check book availability for a date range"""
        try:
            book_uuid = uuid.UUID(book_id)
            
            # Get book info
            book_query = "SELECT * FROM books WHERE book_id = ?"
            book_result = await execute_async(book_query, (book_uuid,))
            
            if not book_result:
                self.set_status(404)
                self.write({"error": "Book not found"})
                return
            
            book = book_result[0]
            
            # Get active reservations for this book
            reservations_query = """
                SELECT * FROM reservations_by_book 
                WHERE book_id = ? AND status = 'active'
            """
            reservations_result = await execute_async(reservations_query, (book_uuid,))
            
            active_reservations = []
            for row in reservations_result:
                active_reservations.append({
                    "reservation_id": str(row.reservation_id),
                    "user_id": str(row.user_id),
                    "user_name": row.user_name,
                    "reservation_date": row.reservation_date.isoformat(),
                    "return_deadline": row.return_deadline.isoformat()
                })
            
            is_available = book.status == 'available' and len(active_reservations) == 0
            
            self.write({
                "book_id": str(book_uuid),
                "title": book.title,
                "status": book.status,
                "is_available": is_available,
                "active_reservations": active_reservations,
                "active_reservations_count": len(active_reservations)
            })
            
        except ValueError:
            self.set_status(400)
            self.write({"error": "Invalid book ID format"})
        except Exception as e:
            logger.error(f"Error checking book availability: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})

class UserHandler(BaseHandler):
    async def post(self):
        """Create a new user"""
        try:
            data = json.loads(self.request.body)
            
            if 'username' not in data:
                self.set_status(400)
                self.write({"error": "Missing required field: username"})
                return
            
            # Check if username already exists (this requires ALLOW FILTERING in Cassandra)
            # In production, consider using a separate table for username lookups
            check_query = "SELECT user_id FROM users WHERE username = ? ALLOW FILTERING"
            existing_result = await execute_async(check_query, (data['username'],))
            
            if existing_result:
                self.set_status(400)
                self.write({"error": "Username already exists"})
                return
            
            user_id = uuid.uuid4()
            now = datetime.utcnow()
            
            query = """
                INSERT INTO users (user_id, username, created_at)
                VALUES (?, ?, ?)
            """
            
            await execute_async(query, (user_id, data['username'], now))
            
            self.set_status(201)
            self.write({
                "user_id": str(user_id),
                "username": data['username'],
                "created_at": now.isoformat()
            })
            
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"error": "Invalid JSON"})
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})

    async def get(self, user_id=None):
        """Get user information"""
        try:
            if not user_id:
                self.set_status(400)
                self.write({"error": "User ID is required"})
                return
                
            user_uuid = uuid.UUID(user_id)
            
            query = "SELECT * FROM users WHERE user_id = ?"
            result = await execute_async(query, (user_uuid,))
            
            if not result:
                self.set_status(404)
                self.write({"error": "User not found"})
                return
            
            user = result[0]
            self.write({
                "user_id": str(user.user_id),
                "username": user.username,
                "created_at": user.created_at.isoformat()
            })
            
        except ValueError:
            self.set_status(400)
            self.write({"error": "Invalid user ID format"})
        except Exception as e:
            logger.error(f"Error fetching user: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})