#!/usr/bin/env python3
"""
Cassandra Keyspace and Tables Setup Script
This script creates the keyspace and all required tables for the library
reservation system.

Usage: python setup_database.py

Make sure Cassandra is running before executing this script.
"""

from cassandra.cluster import Cluster  # type: ignore
from cassandra.policies import DCAwareRoundRobinPolicy
# from cassandra.auth import PlainTextAuthProvider  # type: ignore
import sys
import time


def create_keyspace_and_tables():
    """Create keyspace and all required tables"""

    print("Library Reservation System - Database Setup")
    print("=" * 50)

    try:
        print("Connecting to Cassandra cluster...")
        cluster = Cluster(
            contact_points=[('127.0.0.1', 9042), ('127.0.0.1', 9043)],
            connect_timeout=10,
            load_balancing_policy=DCAwareRoundRobinPolicy(),
            protocol_version=5
        )
        session = cluster.connect()
        print("✓ Connected to Cassandra cluster")
    except Exception as e:
        print(f"✗ Failed to connect to Cassandra: {e}")
        print("Make sure Cassandra is running and accessible.")
        return False

    try:
        print("\nCreating keyspace 'data'...")

        keyspace_query = """
        CREATE KEYSPACE IF NOT EXISTS data
        WITH REPLICATION = {
            'class': 'SimpleStrategy',
            'replication_factor': 2
        }
        """

        session.execute(keyspace_query)
        print("✓ Keyspace 'data' created successfully")
        session.set_keyspace('data')
        print("✓ Connected to keyspace 'data'")

        # Create tables
        tables = {
            "reservations": """
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

            "reservations_by_user": """
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

            "reservations_by_book": """
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

            "books": """
                CREATE TABLE IF NOT EXISTS books (
                    book_id UUID PRIMARY KEY,
                    title TEXT,
                    status TEXT,
                    created_at TIMESTAMP
                )
            """,

            "users": """
                CREATE TABLE IF NOT EXISTS users (
                    user_id UUID PRIMARY KEY,
                    username TEXT,
                    created_at TIMESTAMP
                )
            """
        }

        print("\nCreating tables...")
        for table_name, table_query in tables.items():
            try:
                session.execute(table_query)
                print(f"✓ Table '{table_name}' created successfully")
                time.sleep(0.1)  # Small delay to avoid overwhelming Cassandra
            except Exception as e:
                print(f"✗ Failed to create table '{table_name}': {e}")
                return False

        # Verify tables were created
        print("\nVerifying table creation...")

        # Get list of tables in the keyspace
        tables_query = """
            SELECT table_name FROM system_schema.tables
            WHERE keyspace_name = 'data'
        """

        result = session.execute(tables_query)
        created_tables = [row.table_name for row in result]

        expected_tables = [
            'reservations',
            'reservations_by_user',
            'reservations_by_book',
            'books',
            'users'
        ]

        print("Tables found in keyspace 'data':")
        for table in created_tables:
            status = "✓" if table in expected_tables else "?"
            print(f"  {status} {table}")

        missing_tables = set(expected_tables) - set(created_tables)
        if missing_tables:
            print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
            return False

        print("\n🎉 Database setup completed successfully!")
        print("Created keyspace: data")
        print(f"Created tables: {len(expected_tables)}")

        # Show some additional info
        print("\n📋 Keyspace Information:")
        keyspace_info = session.execute("""
            SELECT * FROM system_schema.keyspaces
            WHERE keyspace_name = 'data'
        """)

        for row in keyspace_info:
            print(f"  Keyspace: {row.keyspace_name}")
            print(f"  Replication: {row.replication}")

        return True

    except Exception as e:
        print(f"✗ Error during database setup: {e}")
        return False

    finally:
        if 'cluster' in locals():
            cluster.shutdown()
            print("\n🔌 Disconnected from Cassandra")


def check_cassandra_connection():
    """Check if Cassandra is accessible"""
    try:
        cluster = Cluster(['127.0.0.1'])
        session = cluster.connect()

        # Try a simple query
        result = session.execute("SELECT release_version FROM system.local")
        version = list(result)[0].release_version

        cluster.shutdown()
        return True, version

    except Exception as e:
        return False, str(e)


def show_connection_info():
    """Show connection information and tips"""
    print("\n📡 Cassandra Connection Information:")
    print("  Trying to connect to: 127.0.0.1:9042, 127.0.0.1:9043")
    print("  Keyspace: data")
    print("  Replication Strategy: SimpleStrategy")
    print("  Replication Factor: 2")

    print("\n🔧 If connection fails, check:")
    print("  1. Cassandra service is running")
    print("  2. Ports 9042 and 9043 are accessible")
    print("  3. IP addresses match your Cassandra nodes")
    print("  4. No authentication is required (or update script)")


def main():
    """Main function"""
    print("Checking Cassandra connection...")

    is_connected, info = check_cassandra_connection()

    if is_connected:
        print(f"✓ Cassandra is accessible (version: {info})")

        if create_keyspace_and_tables():
            print("\n✅ Setup completed successfully!")
            print("\nYou can now run your application:")
            print("  cd backend")
            print("  python app/main.py")

            print("\nOr create sample data:")
            print("  python create_sample_data.py")

        else:
            print("\n❌ Setup failed!")
            sys.exit(1)
    else:
        print(f"✗ Cannot connect to Cassandra: {info}")
        show_connection_info()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
