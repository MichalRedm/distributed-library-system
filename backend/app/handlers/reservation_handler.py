import tornado.web
import json
import uuid
from datetime import datetime, timedelta
from cassandra.cluster import NoHostAvailable
from cassandra import InvalidRequest
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

class ReservationHandler(BaseHandler):
    async def post(self):
        """Create a new reservation"""
        try:
            data = json.loads(self.request.body)
            
            # Validate required fields
            required_fields = ['user_id', 'book_id']
            for field in required_fields:
                if field not in data:
                    self.set_status(400)
                    self.write({"error": f"Missing required field: {field}"})
                    return
            
            user_id = uuid.UUID(data['user_id'])
            book_id = uuid.UUID(data['book_id'])
            
            # Check if user exists
            user_query = "SELECT username FROM users WHERE user_id = %s"
            user_result = await execute_async(user_query, (user_id,))
            if not user_result:
                self.set_status(404)
                self.write({"error": "User not found"})
                return
            
            user_name = user_result[0].username
            
            # Check if book exists and is available
            book_query = "SELECT title, status FROM books WHERE book_id = %s"
            book_result = await execute_async(book_query, (book_id,))
            if not book_result:
                self.set_status(404)
                self.write({"error": "Book not found"})
                return
            
            book_title = book_result[0].title
            book_status = book_result[0].status
            
            if book_status != 'available':
                self.set_status(400)
                self.write({"error": "Book is not available for reservation"})
                return
            
            # Check if user already has an active reservation for this book
            existing_reservation_query = """
                SELECT reservation_id FROM reservations_by_user 
                WHERE user_id = %s AND book_id = %s AND status = 'active'
            """
            existing_result = await execute_async(existing_reservation_query, (user_id, book_id))
            if existing_result:
                self.set_status(400)
                self.write({"error": "User already has an active reservation for this book"})
                return
            
            # Create reservation
            reservation_id = uuid.uuid4()
            now = datetime.utcnow()
            return_deadline = now + timedelta(days=14)  # 2 weeks default
            
            # Insert into all three tables
            reservation_data = {
                'reservation_id': reservation_id,
                'user_id': user_id,
                'book_id': book_id,
                'user_name': user_name,
                'book_title': book_title,
                'status': 'active',
                'reservation_date': now,
                'return_deadline': return_deadline,
                'created_at': now,
                'updated_at': now
            }
            
            # Insert into main reservations table
            insert_reservation = """
                INSERT INTO reservations (reservation_id, user_id, book_id, user_name, book_title, 
                                        status, reservation_date, return_deadline, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Insert into reservations_by_user table
            insert_by_user = """
                INSERT INTO reservations_by_user (user_id, reservation_id, book_id, book_title, 
                                                 status, reservation_date, return_deadline)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            # Insert into reservations_by_book table
            insert_by_book = """
                INSERT INTO reservations_by_book (book_id, reservation_id, user_id, user_name, 
                                                 status, reservation_date, return_deadline)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            # Update book status
            update_book = "UPDATE books SET status = 'checked_out' WHERE book_id = %s"
            
            # Execute all queries
            await execute_async(insert_reservation, (
                reservation_id, user_id, book_id, user_name, book_title,
                'active', now, return_deadline, now, now
            ))
            
            await execute_async(insert_by_user, (
                user_id, reservation_id, book_id, book_title,
                'active', now, return_deadline
            ))
            
            await execute_async(insert_by_book, (
                book_id, reservation_id, user_id, user_name,
                'active', now, return_deadline
            ))
            
            await execute_async(update_book, (book_id,))
            
            self.set_status(201)
            self.write({
                "reservation_id": str(reservation_id),
                "user_id": str(user_id),
                "book_id": str(book_id),
                "user_name": user_name,
                "book_title": book_title,
                "status": "active",
                "reservation_date": now.isoformat(),
                "return_deadline": return_deadline.isoformat(),
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            })
            
        except ValueError as e:
            self.set_status(400)
            self.write({"error": f"Invalid UUID format: {str(e)}"})
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"error": "Invalid JSON"})
        except Exception as e:
            logger.error(f"Error creating reservation: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})

class ReservationDetailHandler(BaseHandler):
    async def get(self, reservation_id):
        """Get a specific reservation"""
        try:
            reservation_uuid = uuid.UUID(reservation_id)
            
            query = "SELECT * FROM reservations WHERE reservation_id = %s"
            result = await execute_async(query, (reservation_uuid,))
            
            if not result:
                self.set_status(404)
                self.write({"error": "Reservation not found"})
                return
            
            reservation = result[0]
            self.write({
                "reservation_id": str(reservation.reservation_id),
                "user_id": str(reservation.user_id),
                "book_id": str(reservation.book_id),
                "user_name": reservation.user_name,
                "book_title": reservation.book_title,
                "status": reservation.status,
                "reservation_date": reservation.reservation_date.isoformat(),
                "return_deadline": reservation.return_deadline.isoformat(),
                "created_at": reservation.created_at.isoformat(),
                "updated_at": reservation.updated_at.isoformat()
            })
            
        except ValueError:
            self.set_status(400)
            self.write({"error": "Invalid reservation ID format"})
        except Exception as e:
            logger.error(f"Error fetching reservation: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})

    async def put(self, reservation_id):
        """Update a reservation"""
        try:
            reservation_uuid = uuid.UUID(reservation_id)
            data = json.loads(self.request.body)
            
            # Check if reservation exists
            query = "SELECT * FROM reservations WHERE reservation_id = %s"
            result = await execute_async(query, (reservation_uuid,))
            
            if not result:
                self.set_status(404)
                self.write({"error": "Reservation not found"})
                return
            
            reservation = result[0]
            now = datetime.utcnow()
            
            # Determine what to update
            updates = {}
            if 'status' in data:
                if data['status'] not in ['active', 'completed']:
                    self.set_status(400)
                    self.write({"error": "Invalid status. Must be 'active' or 'completed'"})
                    return
                updates['status'] = data['status']
            
            if 'return_deadline' in data:
                try:
                    updates['return_deadline'] = datetime.fromisoformat(data['return_deadline'].replace('Z', '+00:00'))
                except ValueError:
                    self.set_status(400)
                    self.write({"error": "Invalid return_deadline format. Use ISO format"})
                    return
            
            if not updates:
                self.set_status(400)
                self.write({"error": "No valid fields to update"})
                return
            
            # Update main reservation
            update_fields = []
            update_values = []
            
            for field, value in updates.items():
                update_fields.append(f"{field} = %s")
                update_values.append(value)
            
            update_fields.append("updated_at = %s")
            update_values.append(now)
            update_values.append(reservation_uuid)
            
            update_query = f"UPDATE reservations SET {', '.join(update_fields)} WHERE reservation_id = %s"
            await execute_async(update_query, update_values)
            
            # Update denormalized tables if status changed
            if 'status' in updates:
                update_by_user = "UPDATE reservations_by_user SET status = %s WHERE user_id = %s AND reservation_id = %s"
                await execute_async(update_by_user, (updates['status'], reservation.user_id, reservation_uuid))
                
                update_by_book = "UPDATE reservations_by_book SET status = %s WHERE book_id = %s AND reservation_id = %s"
                await execute_async(update_by_book, (updates['status'], reservation.book_id, reservation_uuid))
                
                # If marking as completed, make book available again
                if updates['status'] == 'completed':
                    update_book = "UPDATE books SET status = 'available' WHERE book_id = %s"
                    await execute_async(update_book, (reservation.book_id,))
            
            # Return updated reservation
            updated_reservation = await execute_async(query, (reservation_uuid,))
            reservation = updated_reservation[0]
            
            self.write({
                "reservation_id": str(reservation.reservation_id),
                "user_id": str(reservation.user_id),
                "book_id": str(reservation.book_id),
                "user_name": reservation.user_name,
                "book_title": reservation.book_title,
                "status": reservation.status,
                "reservation_date": reservation.reservation_date.isoformat(),
                "return_deadline": reservation.return_deadline.isoformat(),
                "created_at": reservation.created_at.isoformat(),
                "updated_at": reservation.updated_at.isoformat()
            })
            
        except ValueError as e:
            self.set_status(400)
            self.write({"error": f"Invalid format: {str(e)}"})
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"error": "Invalid JSON"})
        except Exception as e:
            logger.error(f"Error updating reservation: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})

class BulkReservationHandler(BaseHandler):
    async def delete(self):
        """Cancel multiple reservations"""
        try:
            data = json.loads(self.request.body)
            
            if 'reservation_ids' not in data or not isinstance(data['reservation_ids'], list):
                self.set_status(400)
                self.write({"error": "reservation_ids must be a list"})
                return
            
            if not data['reservation_ids']:
                self.set_status(400)
                self.write({"error": "reservation_ids cannot be empty"})
                return
            
            # Convert to UUIDs and validate
            reservation_uuids = []
            for res_id in data['reservation_ids']:
                try:
                    reservation_uuids.append(uuid.UUID(res_id))
                except ValueError:
                    self.set_status(400)
                    self.write({"error": f"Invalid reservation ID format: {res_id}"})
                    return
            
            # Fetch all reservations to cancel
            query = "SELECT * FROM reservations WHERE reservation_id IN %s"
            # For Cassandra, we need to query each reservation individually
            reservations_to_cancel = []
            for res_uuid in reservation_uuids:
                single_query = "SELECT * FROM reservations WHERE reservation_id = %s"
                result = await execute_async(single_query, (res_uuid,))
                if result:
                    reservations_to_cancel.extend(result)
            
            if not reservations_to_cancel:
                self.set_status(404)
                self.write({"error": "No reservations found"})
                return
            
            # Cancel each reservation
            cancelled_count = 0
            now = datetime.utcnow()
            
            for reservation in reservations_to_cancel:
                if reservation.status == 'active':
                    # Update main reservation
                    update_main = "UPDATE reservations SET status = 'completed', updated_at = %s WHERE reservation_id = %s"
                    await execute_async(update_main, (now, reservation.reservation_id))
                    
                    # Update denormalized tables
                    update_by_user = "UPDATE reservations_by_user SET status = 'completed' WHERE user_id = %s AND reservation_id = %s"
                    await execute_async(update_by_user, (reservation.user_id, reservation.reservation_id))
                    
                    update_by_book = "UPDATE reservations_by_book SET status = 'completed' WHERE book_id = %s AND reservation_id = %s"
                    await execute_async(update_by_book, (reservation.book_id, reservation.reservation_id))
                    
                    # Make book available again
                    update_book = "UPDATE books SET status = 'available' WHERE book_id = %s"
                    await execute_async(update_book, (reservation.book_id,))
                    
                    cancelled_count += 1
            
            self.write({
                "message": f"Successfully cancelled {cancelled_count} reservations",
                "cancelled_count": cancelled_count,
                "total_requested": len(reservation_uuids)
            })
            
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"error": "Invalid JSON"})
        except Exception as e:
            logger.error(f"Error cancelling reservations: {str(e)}")
            self.set_status(500)
            self.write({"error": "Internal server error"})