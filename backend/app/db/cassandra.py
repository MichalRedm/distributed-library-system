from typing import Optional
from cassandra.cluster import Cluster, Session  # type: ignore
from cassandra.policies import DCAwareRoundRobinPolicy  # type: ignore
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor


cluster = None
session = None
executor = ThreadPoolExecutor(max_workers=10)

logger = logging.getLogger(__name__)


cluster: Optional[Cluster] = None
session: Optional[Session] = None


async def init_cassandra() -> None:
    global cluster, session
    try:
        cluster = Cluster(
            contact_points=[('127.0.0.1', 9042), ('127.0.0.1', 9043)],
            connect_timeout=10,
            load_balancing_policy=DCAwareRoundRobinPolicy(),
            protocol_version=5
        )

        session = cluster.connect()
        keyspace_query = """
        CREATE KEYSPACE IF NOT EXISTS data
        WITH REPLICATION = {
            'class': 'SimpleStrategy',
            'replication_factor': 2
        }
        """
        session.execute(keyspace_query)

        print("✓ Keyspace 'data' created successfully")
        session = cluster.connect('data')

        # Create tables if they don't exist
        await create_tables()

        print("Connected to Cassandra and tables initialized")
    except Exception as e:
        logger.error(f"Failed to connect to Cassandra: {e}")
        raise


async def close_cassandra() -> None:
    if cluster:
        cluster.shutdown()
        print("Cassandra connection closed")


def get_session() -> Session:
    if session is None:
        raise RuntimeError(
            "Cassandra session is not initialized. "
            "Call init_cassandra() first."
        )
    return session


async def execute_async(query, parameters=None):
    """Execute Cassandra query asynchronously"""
    global session
    if session is None:
        raise RuntimeError(
            "Cassandra session is not initialized. "
            "Call init_cassandra() first."
        )
    loop = asyncio.get_event_loop()
    try:
        if parameters:
            result = await loop.run_in_executor(
                executor, session.execute, query, parameters
            )
        else:
            result = await loop.run_in_executor(
                executor, session.execute, query
            )
        return result
    except Exception as e:
        logger.error(f"Database error during query execution: {e}")
        raise


async def create_tables():
    """Create all necessary tables"""
    tables = [
        """
        CREATE TABLE IF NOT EXISTS reservations (
            reservation_id UUID PRIMARY KEY,
            user_id UUID,
            book_id UUID,
            user_name TEXT,
            book_title TEXT,
            status TEXT,
            reservation_date TIMESTAMP,
            return_deadline TIMESTAMP,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS reservations_by_user (
            user_id UUID,
            reservation_id UUID,
            book_id UUID,
            book_title TEXT,
            status TEXT,
            reservation_date TIMESTAMP,
            return_deadline TIMESTAMP,
            PRIMARY KEY (user_id, reservation_id)
        ) WITH CLUSTERING ORDER BY (reservation_id DESC)
        """,
        """
        CREATE TABLE IF NOT EXISTS reservations_by_book (
            book_id UUID,
            reservation_id UUID,
            user_id UUID,
            user_name TEXT,
            status TEXT,
            reservation_date TIMESTAMP,
            return_deadline TIMESTAMP,
            PRIMARY KEY (book_id, reservation_id)
        ) WITH CLUSTERING ORDER BY (reservation_id DESC)
        """,
        """
        CREATE TABLE IF NOT EXISTS reservations_user_book (
            user_id UUID,
            book_id UUID,
            reservation_id UUID,
            user_name TEXT,
            book_title TEXT,
            reservation_date TIMESTAMP,
            return_deadline TIMESTAMP,
            created_at TIMESTAMP,
            PRIMARY KEY (user_id, book_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS books (
            book_id UUID PRIMARY KEY,
            title TEXT,
            status TEXT,
            created_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id UUID PRIMARY KEY,
            username TEXT,
            created_at TIMESTAMP
        )
        """
    ]

    for table_query in tables:
        try:
            await execute_async(table_query)
        except Exception as e:
            logger.error(f"Failed to create table: {e}")
            raise
