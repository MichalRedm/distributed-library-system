#!/usr/bin/env python3
"""
Sample data creation script for the library reservation system.
Run this script to populate your database with sample users and books for testing.

Usage: python create_sample_data.py
"""

import asyncio
import aiohttp
import json
import uuid

API_BASE = "http://localhost:8000/api"

async def create_sample_data():
    """Create sample users and books for testing"""
    
    async with aiohttp.ClientSession() as session:
        print("Creating sample data...")
        
        # Sample users
        users = [
            {"username": "alice_smith"},
            {"username": "bob_jones"},
            {"username": "carol_white"},
            {"username": "david_brown"},
            {"username": "emma_davis"}
        ]
        
        user_ids = []
        print("\nCreating users...")
        for user_data in users:
            try:
                async with session.post(f"{API_BASE}/users", 
                                      json=user_data,
                                      headers={"Content-Type": "application/json"}) as resp:
                    if resp.status == 201:
                        result = await resp.json()
                        user_ids.append(result['user_id'])
                        print(f"✓ Created user: {user_data['username']} (ID: {result['user_id']})")
                    else:
                        error = await resp.json()
                        print(f"✗ Failed to create user {user_data['username']}: {error}")
            except Exception as e:
                print(f"✗ Error creating user {user_data['username']}: {e}")
        
        # Sample books
        books = [
            {"title": "The Great Gatsby"},
            {"title": "To Kill a Mockingbird"},
            {"title": "1984"},
            {"title": "Pride and Prejudice"},
            {"title": "The Catcher in the Rye"},
            {"title": "Lord of the Flies"},
            {"title": "Animal Farm"},
            {"title": "Brave New World"},
            {"title": "The Hobbit"},
            {"title": "Fahrenheit 451"}
        ]
        
        book_ids = []
        print("\nCreating books...")
        for book_data in books:
            try:
                async with session.post(f"{API_BASE}/books",
                                      json=book_data,
                                      headers={"Content-Type": "application/json"}) as resp:
                    if resp.status == 201:
                        result = await resp.json()
                        book_ids.append(result['book_id'])
                        print(f"✓ Created book: {book_data['title']} (ID: {result['book_id']})")
                    else:
                        error = await resp.json()
                        print(f"✗ Failed to create book {book_data['title']}: {error}")
            except Exception as e:
                print(f"✗ Error creating book {book_data['title']}: {e}")
        
        # Create some sample reservations
        print("\nCreating sample reservations...")
        if user_ids and book_ids:
            # Create a few reservations for testing
            sample_reservations = [
                {"user_id": user_ids[0], "book_id": book_ids[0]},  # Alice reserves The Great Gatsby
                {"user_id": user_ids[1], "book_id": book_ids[1]},  # Bob reserves To Kill a Mockingbird
                {"user_id": user_ids[0], "book_id": book_ids[2]},  # Alice also reserves 1984
            ]
            
            reservation_ids = []
            for reservation_data in sample_reservations:
                try:
                    async with session.post(f"{API_BASE}/reservations",
                                          json=reservation_data,
                                          headers={"Content-Type": "application/json"}) as resp:
                        if resp.status == 201:
                            result = await resp.json()
                            reservation_ids.append(result['reservation_id'])
                            print(f"✓ Created reservation: {result['user_name']} reserved {result['book_title']} (ID: {result['reservation_id']})")
                        else:
                            error = await resp.json()
                            print(f"✗ Failed to create reservation: {error}")
                except Exception as e:
                    print(f"✗ Error creating reservation: {e}")
        
        print(f"\n🎉 Sample data creation complete!")
        print(f"Created {len(user_ids)} users, {len(book_ids)} books")
        
        if user_ids and book_ids:
            print(f"\n📚 You can now test the API with these IDs:")
            print(f"Sample User ID: {user_ids[0]}")
            print(f"Sample Book ID: {book_ids[0]}")
            print(f"\nExample API calls:")
            print(f"curl -X GET {API_BASE}/users/{user_ids[0]}")
            print(f"curl -X GET {API_BASE}/books/{book_ids[0]}")
            print(f"curl -X GET {API_BASE}/reservations/user/{user_ids[0]}")

async def test_api_endpoints():
    """Test some basic API endpoints to verify everything is working"""
    print("\n🔍 Testing API endpoints...")
    
    async with aiohttp.ClientSession() as session:
        # Test hello endpoint
        try:
            async with session.get(f"{API_BASE}/hello") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✓ Hello endpoint: {result['message']}")
                else:
                    print(f"✗ Hello endpoint failed: {resp.status}")
        except Exception as e:
            print(f"✗ Hello endpoint error: {e}")
        
        # Test books list endpoint
        try:
            async with session.get(f"{API_BASE}/books") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✓ Books endpoint: Found {result['total_count']} books")
                else:
                    print(f"✗ Books endpoint failed: {resp.status}")
        except Exception as e:
            print(f"✗ Books endpoint error: {e}")
        
        # Test available books
        try:
            async with session.get(f"{API_BASE}/books?available=true") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    available_count = result['total_count']
                    print(f"✓ Available books endpoint: Found {available_count} available books")
                else:
                    print(f"✗ Available books endpoint failed: {resp.status}")
        except Exception as e:
            print(f"✗ Available books endpoint error: {e}")

if __name__ == "__main__":
    print("Library Reservation System - Sample Data Creator")
    print("=" * 50)
    print("Make sure your server is running on http://localhost:8000")
    print("Press Ctrl+C to cancel\n")
    
    try:
        # First test basic connectivity
        asyncio.run(test_api_endpoints())
        
        # Then create sample data
        asyncio.run(create_sample_data())
        
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. Your Cassandra server is running")
        print("2. Your Python server is running on http://localhost:8000")
        print("3. You have aiohttp installed: pip install aiohttp")