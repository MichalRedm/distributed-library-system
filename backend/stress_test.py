import asyncio
import aiohttp
import json
import uuid
import random
import time
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import logging
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TestResults:
    test_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    start_time: float = 0
    end_time: float = 0
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def average_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    @property
    def total_duration(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def requests_per_second(self) -> float:
        if self.total_duration == 0:
            return 0.0
        return self.total_requests / self.total_duration

class LibraryStressTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.users = []
        self.books = []
        self.reservations = []
        
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector, 
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None) -> Tuple[bool, float, Dict]:
        """Make a single HTTP request and return success, response time, and response data"""
        start_time = time.time()
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == 'GET':
                async with self.session.get(url) as response:
                    response_time = time.time() - start_time
                    response_data = await response.json()
                    return response.status < 400, response_time, response_data
            
            elif method.upper() == 'POST':
                async with self.session.post(url, json=data) as response:
                    response_time = time.time() - start_time
                    response_data = await response.json()
                    return response.status < 400, response_time, response_data
            
            elif method.upper() == 'PUT':
                async with self.session.put(url, json=data) as response:
                    response_time = time.time() - start_time
                    response_data = await response.json()
                    return response.status < 400, response_time, response_data
            
            elif method.upper() == 'DELETE':
                async with self.session.delete(url, json=data) as response:
                    response_time = time.time() - start_time
                    response_data = await response.json()
                    return response.status < 400, response_time, response_data
                    
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Request failed: {str(e)}")
            return False, response_time, {"error": str(e)}
    
    async def setup_test_data(self, num_users: int = 100, num_books: int = 50):
        """Create initial test data - users and books"""
        logger.info(f"Setting up test data: {num_users} users, {num_books} books")
        
        # Create users
        user_tasks = []
        for i in range(num_users):
            user_data = {"username": f"testuser_{i}_{uuid.uuid4().hex[:8]}"}
            user_tasks.append(self.create_user(user_data))
        
        user_results = await asyncio.gather(*user_tasks, return_exceptions=True)
        
        for result in user_results:
            if isinstance(result, Exception):
                logger.error(f"Failed to create user: {result}")
            elif result[0]:  # success
                self.users.append(result[2])
        
        # Create books
        book_tasks = []
        for i in range(num_books):
            book_data = {"title": f"Test Book {i} - {uuid.uuid4().hex[:8]}"}
            book_tasks.append(self.create_book(book_data))
        
        book_results = await asyncio.gather(*book_tasks, return_exceptions=True)
        
        for result in book_results:
            if isinstance(result, Exception):
                logger.error(f"Failed to create book: {result}")
            elif result[0]:  # success
                self.books.append(result[2])
        
        logger.info(f"Created {len(self.users)} users and {len(self.books)} books")
    
    async def create_books_for_test(self, num_books: int, test_name: str) -> List[Dict]:
        """Create a separate pool of books for a specific test"""
        logger.info(f"Creating {num_books} dedicated books for {test_name}")
        
        book_tasks = []
        for i in range(num_books):
            book_data = {"title": f"{test_name} Book {i} - {uuid.uuid4().hex[:8]}"}
            book_tasks.append(self.create_book(book_data))
        
        book_results = await asyncio.gather(*book_tasks, return_exceptions=True)
        
        test_books = []
        for result in book_results:
            if isinstance(result, Exception):
                logger.error(f"Failed to create book for {test_name}: {result}")
            elif result[0]:  # success
                test_books.append(result[2])
        
        logger.info(f"Created {len(test_books)} books for {test_name}")
        return test_books
    
    async def create_user(self, user_data: Dict) -> Tuple[bool, float, Dict]:
        return await self.make_request('POST', '/api/users', user_data)
    
    async def create_book(self, book_data: Dict) -> Tuple[bool, float, Dict]:
        return await self.make_request('POST', '/api/books', book_data)
    
    async def create_reservation(self, user_id: str, book_id: str) -> Tuple[bool, float, Dict]:
        reservation_data = {"user_id": user_id, "book_id": book_id}
        return await self.make_request('POST', '/api/reservations', reservation_data)
    
    async def complete_reservation(self, reservation_id: str) -> Tuple[bool, float, Dict]:
        update_data = {"status": "completed"}
        return await self.make_request('PUT', f'/api/reservations/{reservation_id}', update_data)
    
    async def bulk_cancel_reservations(self, reservation_ids: List[str]) -> Tuple[bool, float, Dict]:
        cancel_data = {"reservation_ids": reservation_ids}
        return await self.make_request('DELETE', '/api/reservations/bulk', cancel_data)

    # STRESS TEST 1: Same request very quickly
    async def stress_test_1_same_request_rapid_fire(self, num_requests: int = 1000) -> TestResults:
        """Make the same request very quickly to test for race conditions"""
        logger.info(f"Starting Stress Test 1: {num_requests} rapid identical requests")
        
        results = TestResults("Stress Test 1: Rapid Fire Same Request")
        results.start_time = time.time()
        
        if not self.users:
            logger.error("No users available for testing")
            return results
        
        # Use first user for all requests
        user_id = self.users[0]['user_id']
        
        # Create tasks for getting user's active reservations (should be fast)
        tasks = []
        for _ in range(num_requests):
            tasks.append(self.make_request('GET', f'/api/users/{user_id}/active-reservations'))
        
        # Execute all requests concurrently
        request_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        results.end_time = time.time()
        
        for result in request_results:
            results.total_requests += 1
            if isinstance(result, Exception):
                results.failed_requests += 1
                results.errors.append(str(result))
            else:
                success, response_time, _ = result
                results.response_times.append(response_time)
                if success:
                    results.successful_requests += 1
                else:
                    results.failed_requests += 1
        
        return results

    # STRESS TEST 2: Multiple clients making random requests
    async def stress_test_2_random_requests(self, num_clients: int = 10, requests_per_client: int = 100) -> TestResults:
        """Multiple clients making random requests"""
        logger.info(f"Starting Stress Test 2: {num_clients} clients, {requests_per_client} requests each")
        
        results = TestResults("Stress Test 2: Random Requests from Multiple Clients")
        results.start_time = time.time()
        
        async def client_worker(client_id: int) -> List[Tuple[bool, float, Dict]]:
            """Each client makes random requests"""
            client_results = []
            
            for _ in range(requests_per_client):
                # Randomly choose request type
                request_type = random.choice([
                    'get_users', 'get_books', 'get_user_reservations', 
                    'get_book_reservations', 'get_active_reservations'
                ])
                
                try:
                    if request_type == 'get_users':
                        result = await self.make_request('GET', '/api/users')
                        
                    elif request_type == 'get_books':
                        available_filter = random.choice([True, False])
                        endpoint = f'/api/books?available={str(available_filter).lower()}'
                        result = await self.make_request('GET', endpoint)
                        
                    elif request_type == 'get_user_reservations' and self.users:
                        user = random.choice(self.users)
                        result = await self.make_request('GET', f'/api/reservations/user/{user["user_id"]}')
                        
                    elif request_type == 'get_book_reservations' and self.books:
                        book = random.choice(self.books)
                        result = await self.make_request('GET', f'/api/reservations/book/{book["book_id"]}')
                        
                    elif request_type == 'get_active_reservations' and self.users:
                        user = random.choice(self.users)
                        result = await self.make_request('GET', f'/api/users/{user["user_id"]}/active-reservations')
                        
                    else:
                        # Fallback to get books
                        result = await self.make_request('GET', '/api/books')
                    
                    client_results.append(result)
                    
                    # Small random delay between requests
                    await asyncio.sleep(random.uniform(0.001, 0.01))
                    
                except Exception as e:
                    client_results.append((False, 0.0, {"error": str(e)}))
            
            return client_results
        
        # Run all clients concurrently
        client_tasks = [client_worker(i) for i in range(num_clients)]
        all_client_results = await asyncio.gather(*client_tasks, return_exceptions=True)
        
        results.end_time = time.time()
        
        # Aggregate results
        for client_results in all_client_results:
            if isinstance(client_results, Exception):
                results.failed_requests += requests_per_client
                results.errors.append(str(client_results))
                results.total_requests += requests_per_client
            else:
                for success, response_time, _ in client_results:
                    results.total_requests += 1
                    results.response_times.append(response_time)
                    if success:
                        results.successful_requests += 1
                    else:
                        results.failed_requests += 1
        
        return results

    # STRESS TEST 3: Two clients trying to reserve all books simultaneously
    async def stress_test_3_book_reservation_race(self) -> TestResults:
        """Two clients trying to reserve all available books at the same time"""
        logger.info("Starting Stress Test 3: Book Reservation Race Condition")
        
        results = TestResults("Stress Test 3: Book Reservation Race")
        results.start_time = time.time()
        
        if len(self.users) < 2 or len(self.books) < 1:
            logger.error("Need at least 2 users and 1 book for this test")
            return results
        
        client1_user = self.users[0]
        client2_user = self.users[1]
        
        async def reservation_client(user: Dict, client_name: str) -> List[Tuple[bool, float, Dict]]:
            """Each client tries to reserve all books"""
            client_results = []
            
            for book in self.books:
                try:
                    result = await self.create_reservation(user['user_id'], book['book_id'])
                    client_results.append(result)
                    
                    # Very small delay to simulate real-world timing
                    await asyncio.sleep(0.001)
                    
                except Exception as e:
                    client_results.append((False, 0.0, {"error": str(e)}))
            
            return client_results
        
        # Run both clients simultaneously
        client1_task = reservation_client(client1_user, "Client1")
        client2_task = reservation_client(client2_user, "Client2")
        
        client1_results, client2_results = await asyncio.gather(
            client1_task, client2_task, return_exceptions=True
        )
        
        results.end_time = time.time()
        
        # Process results from both clients
        for client_results in [client1_results, client2_results]:
            if isinstance(client_results, Exception):
                results.failed_requests += len(self.books)
                results.errors.append(str(client_results))
                results.total_requests += len(self.books)
            else:
                for success, response_time, response_data in client_results:
                    results.total_requests += 1
                    results.response_times.append(response_time)
                    if success:
                        results.successful_requests += 1
                        # Store successful reservations
                        if 'reservation_id' in response_data:
                            self.reservations.append(response_data)
                    else:
                        results.failed_requests += 1
                        if 'error' in response_data:
                            results.errors.append(response_data['error'])
        
        # Log fairness analysis
        client1_successes = sum(1 for success, _, _ in client1_results if success)
        client2_successes = sum(1 for success, _, _ in client2_results if success)
        
        logger.info(f"Client 1 successful reservations: {client1_successes}")
        logger.info(f"Client 2 successful reservations: {client2_successes}")
        logger.info(f"Total books: {len(self.books)}")
        
        return results

    # STRESS TEST 4: Constant completions and reservations (FIXED)
    async def stress_test_4_constant_activity(self, duration_seconds: int = 60) -> TestResults:
        """Constant stream of reservations and completions"""
        logger.info(f"Starting Stress Test 4: Constant activity for {duration_seconds} seconds")
        
        results = TestResults("Stress Test 4: Constant Reservations and Completions")
        results.start_time = time.time()
        
        if len(self.users) < 5:
            logger.error("Need at least 5 users for this test")
            return results
        
        # Create dedicated books for this test (more books to avoid conflicts)
        test4_books = await self.create_books_for_test(50, "Test4")
        
        if len(test4_books) < 10:
            logger.error("Failed to create enough books for Test 4")
            return results
        
        end_time = time.time() + duration_seconds
        active_reservations = []

        available_books = set(book['book_id'] for book in test4_books)
        reserved_books = set()
        
        # Lock for thread-safe access to shared data structures
        lock = asyncio.Lock()
        
        async def reservation_worker():
            """Continuously make new reservations"""
            nonlocal active_reservations, reserved_books, available_books
            
            while time.time() < end_time:
                try:
                    async with lock:
                        available_unreserved = available_books - reserved_books
                        if not available_unreserved:
                            # No books available, wait and continue
                            await asyncio.sleep(0.1)
                            continue
                        
                        book_id = random.choice(list(available_unreserved))
                        reserved_books.add(book_id)
                    
                    user = random.choice(self.users)
                    
                    success, response_time, response_data = await self.create_reservation(
                        user['user_id'], book_id
                    )
                    
                    results.total_requests += 1
                    results.response_times.append(response_time)

                    if success and 'reservation_id' in response_data:
                        results.successful_requests += 1
                        async with lock:
                            # Store both reservation data and the book_id for later cleanup
                            reservation_data = response_data.copy()
                            reservation_data['book_id'] = book_id
                            active_reservations.append(reservation_data)
                    else:
                        results.failed_requests += 1
                        if 'error' in response_data:
                            results.errors.append(response_data['error'])
                        
                        # If reservation failed, free up the book
                        async with lock:
                            reserved_books.discard(book_id)
                    
                    await asyncio.sleep(random.uniform(0.1, 0.5))
                    
                except Exception as e:
                    results.failed_requests += 1
                    results.errors.append(str(e))
                    # Make sure to free up the book if there was an error
                    if 'book_id' in locals():
                        async with lock:
                            reserved_books.discard(book_id)

            print("Reservation worker finished")
        
        async def completion_worker():
            """Continuously complete reservations"""
            nonlocal active_reservations, reserved_books
            
            while time.time() < end_time:
                try:
                    reservation = None
                    async with lock:
                        if active_reservations:
                            reservation = active_reservations.pop(0)
                    
                    if reservation:
                        success, response_time, response_data = await self.complete_reservation(
                            reservation['reservation_id']
                        )
                        
                        results.total_requests += 1
                        results.response_times.append(response_time)
                        
                        if success:
                            results.successful_requests += 1
                            # Free up the book when reservation is completed
                            async with lock:
                                reserved_books.discard(reservation['book_id'])
                        else:
                            results.failed_requests += 1
                            if 'error' in response_data:
                                results.errors.append(response_data['error'])
                            # If completion failed, put the reservation back and keep book reserved
                            async with lock:
                                active_reservations.append(reservation)
                    else:
                        # No reservations to complete, wait a bit
                        await asyncio.sleep(0.1)
                    
                    await asyncio.sleep(random.uniform(0.2, 0.8))
                    
                except Exception as e:
                    results.failed_requests += 1
                    results.errors.append(str(e))

            print("Completion worker finished")
        
        # Run both workers concurrently
        await asyncio.gather(
            reservation_worker(),
            completion_worker(),
            return_exceptions=True
        )
        
        results.end_time = time.time()
        logger.info(f"Test 4 completed with {len(active_reservations)} active reservations remaining")

        return results

    # STRESS TEST 5: Large group cancellation
    async def stress_test_5_bulk_cancellation(self, num_reservations: int = 100) -> TestResults:
        """Create many reservations and then cancel them in bulk"""
        logger.info(f"Starting Stress Test 5: Bulk cancellation of {num_reservations} reservations")
        
        results = TestResults("Stress Test 5: Large Group Cancellation")
        results.start_time = time.time()
        
        # Create dedicated books for this test (ensure we have enough available books)
        books_needed = min(num_reservations, 80)  # Limit to reasonable number
        test5_books = await self.create_books_for_test(books_needed, "Test5")
        
        if len(test5_books) < 10:
            logger.error("Failed to create enough books for Test 5")
            return results
        
        # First, create many reservations
        reservation_tasks = []
        created_reservations = []
        
        used_books = set()
        for i in range(num_reservations):
            if self.users and test5_books:
                user = random.choice(self.users)
                book = random.choice([b for b in test5_books if b['book_id'] not in used_books])
                used_books.add(book['book_id'])
                reservation_tasks.append(self.create_reservation(user['user_id'], book['book_id']))
        
        # Create reservations
        logger.info(f"Creating {len(reservation_tasks)} reservations...")
        reservation_results = await asyncio.gather(*reservation_tasks, return_exceptions=True)
        
        for result in reservation_results:
            results.total_requests += 1
            if isinstance(result, Exception):
                results.failed_requests += 1
                results.errors.append(str(result))
            else:
                success, response_time, response_data = result
                results.response_times.append(response_time)
                if success and 'reservation_id' in response_data:
                    results.successful_requests += 1
                    created_reservations.append(response_data['reservation_id'])
                else:
                    results.failed_requests += 1
        
        logger.info(f"Created {len(created_reservations)} reservations successfully")
        
        # Now perform bulk cancellations in groups
        batch_size = 25  # Cancel in batches of 25
        cancellation_tasks = []
        
        for i in range(0, len(created_reservations), batch_size):
            batch = created_reservations[i:i + batch_size]
            if batch:
                cancellation_tasks.append(self.bulk_cancel_reservations(batch))
        
        # Execute bulk cancellations
        logger.info(f"Performing {len(cancellation_tasks)} bulk cancellation operations...")
        cancellation_results = await asyncio.gather(*cancellation_tasks, return_exceptions=True)
        
        for result in cancellation_results:
            results.total_requests += 1
            if isinstance(result, Exception):
                results.failed_requests += 1
                results.errors.append(str(result))
            else:
                success, response_time, response_data = result
                results.response_times.append(response_time)
                if success:
                    results.successful_requests += 1
                else:
                    results.failed_requests += 1
                    if 'error' in response_data:
                        results.errors.append(response_data['error'])
        
        results.end_time = time.time()
        return results

    def print_results(self, results: TestResults):
        """Print formatted test results"""
        print(f"\n{'='*60}")
        print(f"📊 {results.test_name}")
        print(f"{'='*60}")
        print(f"📈 Total Requests: {results.total_requests}")
        print(f"✅ Successful: {results.successful_requests}")
        print(f"❌ Failed: {results.failed_requests}")
        print(f"📊 Success Rate: {results.success_rate:.2f}%")
        print(f"⏱️  Total Duration: {results.total_duration:.2f} seconds")
        print(f"🚀 Requests/Second: {results.requests_per_second:.2f}")
        
        if results.response_times:
            print(f"📊 Average Response Time: {results.average_response_time:.4f} seconds")
            print(f"📊 Min Response Time: {min(results.response_times):.4f} seconds")
            print(f"📊 Max Response Time: {max(results.response_times):.4f} seconds")
            print(f"📊 Median Response Time: {statistics.median(results.response_times):.4f} seconds")
        
        if results.errors:
            print(f"\n❌ Top Errors:")
            error_counts = {}
            for error in results.errors[:20]:  # Show top 20 errors
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {count}x: {error}")

        # NOTE PRINT ALL ERRORS FOR DEBUGGING DELETE LATER
            for error in results.errors:
                error_counts[error] = error_counts.get(error, 0) + 1

            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {count}x: {error}")
        
        print(f"{'='*60}\n")

    async def run_all_stress_tests(self):
        """Run all stress tests in sequence"""
        logger.info("🚀 Starting Library API Stress Test Suite")
        
        # Setup test data
        await self.setup_test_data(num_users=50, num_books=30)
        
        if not self.users or not self.books:
            logger.error("Failed to create test data. Cannot run stress tests.")
            return
        
        all_results = []
        
        # Test 1: Rapid fire same request
        test1_results = await self.stress_test_1_same_request_rapid_fire(500)
        all_results.append(test1_results)
        self.print_results(test1_results)
        
        # Test 2: Random requests from multiple clients
        test2_results = await self.stress_test_2_random_requests(8, 50)
        all_results.append(test2_results)
        self.print_results(test2_results)
        
        # Test 3: Book reservation race
        test3_results = await self.stress_test_3_book_reservation_race()
        all_results.append(test3_results)
        self.print_results(test3_results)
        
        # Test 4: Constant activity
        test4_results = await self.stress_test_4_constant_activity(30)
        all_results.append(test4_results)
        self.print_results(test4_results)
        
        # Test 5: Bulk cancellation
        test5_results = await self.stress_test_5_bulk_cancellation(80)
        all_results.append(test5_results)
        self.print_results(test5_results)
        
        # Summary
        print(f"\n{'🎯 STRESS TEST SUITE SUMMARY'}")
        print(f"{'='*60}")
        
        total_requests = sum(r.total_requests for r in all_results)
        total_successful = sum(r.successful_requests for r in all_results)
        total_failed = sum(r.failed_requests for r in all_results)
        overall_success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0
        
        print(f"📊 Overall Statistics:")
        print(f"   Total Requests Across All Tests: {total_requests}")
        print(f"   Total Successful: {total_successful}")
        print(f"   Total Failed: {total_failed}")
        print(f"   Overall Success Rate: {overall_success_rate:.2f}%")
        
        print(f"\n📋 Individual Test Performance:")
        for result in all_results:
            print(f"   {result.test_name}: {result.success_rate:.1f}% success, {result.requests_per_second:.1f} req/s")
        
        print(f"{'='*60}")

async def main():
    """Main function to run the stress tests"""
    # You can change the base URL to match your server
    base_url = "http://localhost:8000"
    
    async with LibraryStressTest(base_url) as stress_tester:
        await stress_tester.run_all_stress_tests()

if __name__ == "__main__":
    print("🧪 Library Management System - Stress Test Suite")
    print("=" * 60)
    print("Make sure your library API server is running on http://localhost:8000")
    print("Press Ctrl+C to stop the tests at any time")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚡ Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        logging.exception("Test suite error")