import requests
import uuid

API_BASE = "http://localhost:8000/api"

NUM_USERS = 5
NUM_BOOKS = 5


def create_users():
    users = []
    for i in range(NUM_USERS):
        username = f"user_{i+1}_{uuid.uuid4().hex[:6]}"
        res = requests.post(f"{API_BASE}/users", json={"username": username})
        if res.status_code == 201:
            user = res.json()
            print(f"✅ Created user: {user['username']} ({user['user_id']})")
            users.append(user)
        else:
            print(f"❌ Failed to create user {username}: {res.text}")
    return users


def create_books():
    books = []
    for i in range(NUM_BOOKS):
        title = f"Book {i+1} - {uuid.uuid4().hex[:5]}"
        res = requests.post(f"{API_BASE}/books", json={"title": title})
        if res.status_code in (200, 201):
            book = res.json()
            print(f"📖 Created book: {book['title']} ({book['book_id']})")
            books.append(book)
        else:
            print(f"❌ Failed to create book {title}: {res.text}")
    return books


def make_reservations(users, books):
    num = min(3, len(users), len(books))
    for i in range(num):
        user = users[i]
        book = books[i]
        payload = {
            "user_id": user["user_id"],
            "book_id": book["book_id"]
        }
        res = requests.post(f"{API_BASE}/reservations", json=payload)
        if res.status_code == 201:
            print(
                "📚 Reservation created: "
                f"{user['username']} → {book['title']}"
            )
        else:
            print(f"⚠️ Failed to create reservation: {res.text}")


if __name__ == "__main__":
    print("🔧 Creating sample users and books...\n")
    users = create_users()
    books = create_books()
    print("\n🔁 Creating reservations for first 3 user-book pairs...\n")
    make_reservations(users, books)
    print("\n✅ Sample data setup complete.")
