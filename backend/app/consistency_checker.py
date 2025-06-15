import asyncio
import uuid
from datetime import datetime, timedelta
from db.cassandra import execute_async
import logging
from cassandra.query import SimpleStatement

logger = logging.getLogger(__name__)


class DataConsistencyChecker:
    def __init__(self, check_interval_seconds=10, quiet_period_seconds=15):
        self.check_interval = check_interval_seconds
        # How long to wait after last write before checking
        self.quiet_period = quiet_period_seconds
        self.last_write_time = datetime.utcnow()
        self.last_check_time = datetime.utcnow()
        self.is_running = False
        self.task = None

    def mark_write_activity(self):
        """Call this method whenever a write operation occurs"""
        self.last_write_time = datetime.utcnow()

    async def start_monitoring(self):
        """Start the consistency checker task"""
        if self.is_running:
            logger.warning("Consistency checker is already running")
            return

        self.is_running = True
        self.task = asyncio.create_task(self._monitor_loop())
        logger.info(
            "Data consistency checker started "
            f"(interval: {self.check_interval}s, "
            f"quiet period: {self.quiet_period}s)"
        )

    async def stop_monitoring(self):
        """Stop the consistency checker task"""
        if not self.is_running:
            return

        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Data consistency checker stopped")

    async def _monitor_loop(self):
        """Main monitoring loop"""
        try:
            while self.is_running:
                await asyncio.sleep(self.check_interval)

                now = datetime.utcnow()

                # Check if there was write activity since last check
                write_activity_since_last_check = (
                    self.last_write_time > self.last_check_time
                )

                # Check if enough time has passed
                # since last write (quiet period)
                time_since_last_write = now - self.last_write_time
                quiet_period_elapsed = (
                    time_since_last_write >= timedelta(
                        seconds=self.quiet_period
                    )
                )

                if write_activity_since_last_check and quiet_period_elapsed:
                    logger.info(
                        "Write activity detected since last check "
                        "and quiet period elapsed "
                        f"({time_since_last_write.total_seconds():.1f}s), "
                        "running consistency check..."
                    )
                    await self.run_consistency_check()
                    self.last_check_time = now
                elif write_activity_since_last_check:
                    t = (
                        self.quiet_period
                        - time_since_last_write.total_seconds()
                    )
                    logger.debug(
                        "Write activity detected but still in quiet period "
                        f"(waiting {t:.1f}s more"
                    )

        except asyncio.CancelledError:
            logger.info("Consistency checker task cancelled")
        except Exception as e:
            logger.error(f"Error in consistency checker loop: {e}")

    async def run_consistency_check(self):
        """Main consistency check function"""
        try:
            logger.info("Starting data consistency check...")

            # Load all data into memory first to avoid inefficient queries
            data = await self._load_all_data()

            # Step 1: Fix duplicate reservations in reservations_user_book
            duplicates_fixed = await self._fix_duplicate_active_reservations(
                data
            )

            # Step 2: Sync book statuses with active reservations
            book_status_fixes = await self._sync_book_statuses(data)

            # Step 3: Sync reservation statuses across all tables
            reservation_status_fixes = await self._sync_reservation_statuses(
                data
            )

            # Step 4: Final validation
            await self._validate_final_state(data)

            if (
                duplicates_fixed > 0
                or book_status_fixes > 0
                or reservation_status_fixes > 0
            ):
                logger.warning(
                    f"Consistency check completed. Fixed: "
                    f"{duplicates_fixed} duplicates, "
                    f"{book_status_fixes} book statuses, "
                    f"{reservation_status_fixes} reservation statuses"
                )
            else:
                logger.info("Consistency check completed. No issues found.")

        except Exception as e:
            logger.error(f"Error during consistency check: {e}")

    async def _load_all_data(self):
        """Load all relevant data into memory to avoid inefficient queries"""
        try:
            logger.debug("Loading all data into memory...")

            # Load all tables with simple SELECT * queries (no filtering)
            active_reservations = await execute_async(
                SimpleStatement(
                    "SELECT * FROM reservations_user_book",
                    fetch_size=100
                )
            )
            all_reservations = await execute_async(
                "SELECT * FROM reservations"
            )
            all_books = await execute_async("SELECT * FROM books")
            reservations_by_user = await execute_async(
                "SELECT * FROM reservations_by_user"
            )
            reservations_by_book = await execute_async(
                "SELECT * FROM reservations_by_book"
            )

            return {
                'active_reservations': (
                    list(active_reservations) if active_reservations else []
                ),
                'all_reservations': (
                    list(all_reservations) if all_reservations else []
                ),
                'all_books': (
                    list(all_books) if all_books else []
                ),
                'reservations_by_user': (
                    list(reservations_by_user) if reservations_by_user else []
                ),
                'reservations_by_book': (
                    list(reservations_by_book) if reservations_by_book else []
                )
            }

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return {
                'active_reservations': [],
                'all_reservations': [],
                'all_books': [],
                'reservations_by_user': [],
                'reservations_by_book': []
            }

    async def _fix_duplicate_active_reservations(self, data):
        """Fix cases where a book is reserved by multiple users"""
        fixed_count = 0

        try:
            active_reservations = data['active_reservations']

            # Group by book_id to find duplicates
            book_reservations = {}
            for row in active_reservations:
                book_id = str(row.book_id)
                if book_id not in book_reservations:
                    book_reservations[book_id] = []
                book_reservations[book_id].append({
                    'user_id': row.user_id,
                    'reservation_id': row.reservation_id,
                    'reservation_date': row.reservation_date
                })

            # Find books with multiple active reservations
            for book_id, reservations in book_reservations.items():
                if len(reservations) > 1:
                    logger.warning(
                        f"Found {len(reservations)} active "
                        f"reservations for book {book_id}"
                    )

                    # Keep the earliest reservation, cancel others
                    reservations.sort(key=lambda x: x['reservation_date'])
                    keep_reservation = reservations[0]
                    cancel_reservations = reservations[1:]

                    logger.info(
                        "Keeping reservation "
                        f"{keep_reservation['reservation_id']}, "
                        f"cancelling {len(cancel_reservations)} others"
                    )

                    # Cancel the duplicate reservations
                    for reservation in cancel_reservations:
                        await self._cancel_reservation(
                            reservation['reservation_id'],
                            reservation['user_id'],
                            uuid.UUID(book_id)
                        )
                        fixed_count += 1

            return fixed_count

        except Exception as e:
            logger.error(f"Error fixing duplicate reservations: {e}")
            return 0

    async def _cancel_reservation(self, reservation_id, user_id, book_id):
        """Cancel a specific reservation and update all tables"""
        try:
            now = datetime.utcnow()

            # Update main reservations table
            update_main = """
                UPDATE reservations
                SET status = 'completed', updated_at = %s
                WHERE reservation_id = %s
            """
            await execute_async(update_main, (now, reservation_id))

            # Update reservations_by_user table
            update_by_user = """
                UPDATE reservations_by_user
                SET status = 'completed'
                WHERE user_id = %s AND reservation_id = %s
            """
            await execute_async(update_by_user, (user_id, reservation_id))

            # Update reservations_by_book table
            update_by_book = """
                UPDATE reservations_by_book
                SET status = 'completed'
                WHERE book_id = %s AND reservation_id = %s
            """
            await execute_async(update_by_book, (book_id, reservation_id))

            # Remove from active reservations table
            delete_active = """
                DELETE FROM reservations_user_book
                WHERE user_id = %s AND book_id = %s
            """
            await execute_async(delete_active, (user_id, book_id))

            logger.info(f"Cancelled duplicate reservation {reservation_id}")

        except Exception as e:
            logger.error(f"Error cancelling reservation {reservation_id}: {e}")

    async def _sync_book_statuses(self, data):
        """Ensure book statuses match active reservations"""
        fixed_count = 0

        try:
            all_books = data['all_books']
            active_reservations = data['active_reservations']

            # Create set of active book IDs for O(1) lookup
            active_book_ids = {str(row.book_id) for row in active_reservations}

            for book in all_books:
                book_id_str = str(book.book_id)
                current_status = book.status
                should_be_checked_out = book_id_str in active_book_ids

                # Fix status if inconsistent
                if should_be_checked_out and current_status != 'checked_out':
                    logger.warning(
                        f"Book {book_id_str} ({book.title}) should "
                        f"be checked_out but is '{current_status}'"
                    )
                    update_query = (
                        "UPDATE books SET status = 'checked_out' "
                        "WHERE book_id = %s"
                    )
                    await execute_async(update_query, (book.book_id,))
                    fixed_count += 1

                elif (
                    not should_be_checked_out
                    and current_status != 'available'
                ):
                    logger.warning(
                        f"Book {book_id_str} ({book.title}) should "
                        f"be available but is '{current_status}'"
                    )
                    update_query = (
                        "UPDATE books SET status = 'available' "
                        "WHERE book_id = %s"
                    )
                    await execute_async(update_query, (book.book_id,))
                    fixed_count += 1

            return fixed_count

        except Exception as e:
            logger.error(f"Error syncing book statuses: {e}")
            return 0

    async def _sync_reservation_statuses(self, data):
        """Ensure reservation statuses are consistent across all tables"""
        fixed_count = 0

        try:
            active_reservations = data['active_reservations']
            all_reservations = data['all_reservations']
            reservations_by_user = data['reservations_by_user']
            reservations_by_book = data['reservations_by_book']

            # Create set of active reservation IDs for O(1) lookup
            active_reservation_ids = {
                str(row.reservation_id)
                for row in active_reservations
            }

            # Check main reservations table
            for reservation in all_reservations:
                reservation_id_str = str(reservation.reservation_id)
                should_be_active = reservation_id_str in active_reservation_ids
                current_status = reservation.status

                if should_be_active and current_status != 'active':
                    logger.warning(
                        f"Reservation {reservation_id_str} should be "
                        f"active but is '{current_status}'"
                    )
                    update_query = """
                        UPDATE reservations
                        SET status = 'active', updated_at = %s
                        WHERE reservation_id = %s
                    """
                    await execute_async(
                        update_query,
                        (datetime.utcnow(), reservation.reservation_id)
                    )
                    fixed_count += 1

                elif not should_be_active and current_status == 'active':
                    logger.warning(
                        f"Reservation {reservation_id_str} should be "
                        "completed but is active"
                    )
                    update_query = """
                        UPDATE reservations
                        SET status = 'completed', updated_at = %s
                        WHERE reservation_id = %s
                    """
                    await execute_async(
                        update_query,
                        (datetime.utcnow(), reservation.reservation_id)
                    )
                    fixed_count += 1

            # Check reservations_by_user table
            for reservation in reservations_by_user:
                reservation_id_str = str(reservation.reservation_id)
                should_be_active = reservation_id_str in active_reservation_ids
                current_status = reservation.status

                if should_be_active and current_status != 'active':
                    update_query = """
                        UPDATE reservations_by_user
                        SET status = 'active'
                        WHERE user_id = %s AND reservation_id = %s
                    """
                    await execute_async(
                        update_query,
                        (reservation.user_id, reservation.reservation_id)
                    )
                    fixed_count += 1

                elif not should_be_active and current_status == 'active':
                    update_query = """
                        UPDATE reservations_by_user
                        SET status = 'completed'
                        WHERE user_id = %s AND reservation_id = %s
                    """
                    await execute_async(
                        update_query,
                        (reservation.user_id, reservation.reservation_id)
                    )
                    fixed_count += 1

            # Check reservations_by_book table
            for reservation in reservations_by_book:
                reservation_id_str = str(reservation.reservation_id)
                should_be_active = reservation_id_str in active_reservation_ids
                current_status = reservation.status

                if should_be_active and current_status != 'active':
                    update_query = """
                        UPDATE reservations_by_book
                        SET status = 'active'
                        WHERE book_id = %s AND reservation_id = %s
                    """
                    await execute_async(
                        update_query,
                        (reservation.book_id, reservation.reservation_id)
                    )
                    fixed_count += 1

                elif not should_be_active and current_status == 'active':
                    update_query = """
                        UPDATE reservations_by_book
                        SET status = 'completed'
                        WHERE book_id = %s AND reservation_id = %s
                    """
                    await execute_async(
                        update_query,
                        (reservation.book_id, reservation.reservation_id)
                    )
                    fixed_count += 1

            return fixed_count

        except Exception as e:
            logger.error(f"Error syncing reservation statuses: {e}")
            return 0

    async def _validate_final_state(self, data):
        """Final validation to ensure everything is consistent"""
        try:
            active_reservations = data['active_reservations']
            all_books = data['all_books']

            # Count active reservations and checked out books
            user_book_count = len(active_reservations)
            checked_out_books = [
                book for book in all_books
                if book.status == 'checked_out'
            ]
            checked_count = len(checked_out_books)

            logger.info("Final state validation:")
            logger.info(
                "  Active reservations in user_book "
                f"table: {user_book_count}"
            )
            logger.info(f"  Checked out books: {checked_count}")

            # These counts should match
            if user_book_count != checked_count:
                logger.error(
                    "CONSISTENCY ERROR: "
                    "Active reservations ({user_book_count}) "
                    "don't match checked out books ({checked_count})"
                )
            else:
                logger.info(
                    "✅ Active reservations match checked out "
                    "books - core data is consistent"
                )

            # Check for duplicate active reservations
            # (books reserved by multiple users)
            book_reservation_count = {}
            for reservation in active_reservations:
                book_id = str(reservation.book_id)
                book_reservation_count[book_id] = (
                    book_reservation_count.get(book_id, 0) + 1
                )

            duplicates_found = 0
            for book_id, count in book_reservation_count.items():
                if count > 1:
                    logger.error(
                        f"DUPLICATE RESERVATION: Book {book_id} "
                        f"has {count} active reservations"
                    )
                    duplicates_found += 1

            if duplicates_found == 0:
                logger.info("✅ No duplicate active reservations found")
            else:
                logger.error(
                    f"❌ Found {duplicates_found} books "
                    "with duplicate active reservations"
                )

        except Exception as e:
            logger.error(f"Error during final validation: {e}")


# Global instance
consistency_checker = DataConsistencyChecker()


async def start_consistency_checker():
    """Start the global consistency checker"""
    await consistency_checker.start_monitoring()


async def stop_consistency_checker():
    """Stop the global consistency checker"""
    await consistency_checker.stop_monitoring()


def mark_write_activity():
    """Mark that a write operation occurred - call this from your handlers"""
    consistency_checker.mark_write_activity()
