# Backend API Documentation

This document describes the API endpoints provided by the backend of the Library Reservation System.

> **Note:**  
> Setup instructions, license, and general project information are located in the root `README.md`.

---

## Base URL

```

/api/

```

All endpoints are relative to this prefix.

---

## Endpoints

### Users

#### Get all users

```

GET /api/users

````

**Response**
```json
{
  "users": [
    {
      "user_id": "uuid",
      "username": "string",
      "created_at": "ISO8601 timestamp"
    }
  ],
  "total_count": integer
}
````

#### Get user by ID

```
GET /api/users/{user_id}
```

**Response**

```json
{
  "user_id": "uuid",
  "username": "string",
  "created_at": "ISO8601 timestamp",
  "active_reservations_count": integer
}
```

#### Create new user

```
POST /api/users
Content-Type: application/json
```

**Request body**

```json
{
  "username": "string"
}
```

**Response (201 Created)**

```json
{
  "user_id": "uuid",
  "username": "string",
  "created_at": "ISO8601 timestamp"
}
```

#### Get active reservations for a user

```
GET /api/users/{user_id}/active-reservations
```

**Response**

```json
{
  "user_id": "uuid",
  "username": "string",
  "active_reservations": [
    {
      "reservation_id": "uuid",
      "book_id": "uuid",
      "book_title": "string",
      "reservation_date": "ISO8601 timestamp",
      "return_deadline": "ISO8601 timestamp",
      "created_at": "ISO8601 timestamp"
    }
  ],
  "active_count": integer
}
```

---

### Books

#### Get all books

```
GET /api/books
```

Optional query parameter:

* `available=true` — only return available books

**Response**

```json
{
  "books": [
    {
      "book_id": "uuid",
      "title": "string",
      "status": "available" | "checked_out",
      "created_at": "ISO8601 timestamp"
    }
  ],
  "total_count": integer,
  "filter_applied": "available_only" | "none"
}
```

#### Get book by ID

```
GET /api/books/{book_id}
```

**Response**

```json
{
  "book_id": "uuid",
  "title": "string",
  "status": "available" | "checked_out",
  "created_at": "ISO8601 timestamp"
}
```

#### Create new book

```
POST /api/books
Content-Type: application/json
```

**Request body**

```json
{
  "title": "string"
}
```

**Response (201 Created)**

```json
{
  "book_id": "uuid",
  "title": "string",
  "status": "available",
  "created_at": "ISO8601 timestamp"
}
```

#### Check book availability

```
GET /api/books/{book_id}/availability
```

**Response**

```json
{
  "book_id": "uuid",
  "available": true | false,
  "status": "available" | "checked_out"
}
```

---

### Reservations

#### Make a reservation

```
POST /api/reservations
Content-Type: application/json
```

**Request body**

```json
{
  "user_id": "uuid",
  "book_id": "uuid"
}
```

**Response (201 Created)**

```json
{
  "reservation_id": "uuid",
  "user_id": "uuid",
  "book_id": "uuid",
  "user_name": "string",
  "book_title": "string",
  "status": "active",
  "reservation_date": "ISO8601 timestamp",
  "return_deadline": "ISO8601 timestamp",
  "created_at": "ISO8601 timestamp",
  "updated_at": "ISO8601 timestamp"
}
```

#### Get specific reservation

```
GET /api/reservations/{id}
```

**Response**

```json
{
  "reservation_id": "uuid",
  "user_id": "uuid",
  "book_id": "uuid",
  "user_name": "string",
  "book_title": "string",
  "status": "active" | "completed",
  "reservation_date": "ISO8601 timestamp",
  "return_deadline": "ISO8601 timestamp",
  "created_at": "ISO8601 timestamp",
  "updated_at": "ISO8601 timestamp"
}
```

#### Update reservation

```
PUT /api/reservations/{id}
Content-Type: application/json
```

**Request body**

```json
{
  "status": "active" | "completed",
  "return_deadline": "ISO8601 timestamp"
}
```

**Response**

```json
{
  "reservation_id": "uuid",
  "user_id": "uuid",
  "book_id": "uuid",
  "user_name": "string",
  "book_title": "string",
  "status": "active" | "completed",
  "reservation_date": "ISO8601 timestamp",
  "return_deadline": "ISO8601 timestamp",
  "created_at": "ISO8601 timestamp",
  "updated_at": "ISO8601 timestamp"
}
```

#### Cancel multiple reservations

```
DELETE /api/reservations/bulk
Content-Type: application/json
```

**Request body**

```json
{
  "reservation_ids": ["uuid", "uuid", ...]
}
```

**Response**

```json
{
  "message": "Successfully cancelled {count} reservations",
  "cancelled_count": integer,
  "total_requested": integer
}
```

#### Get user's ALL reservations

```
GET /api/reservations/user/{user_id}
```

**Response**
```json
{
  "user_id": "uuid",
  "username": "string",
  "reservations": [
    {
      "reservation_id": "uuid",
      "book_id": "uuid",
      "book_title": "string",
      "status": "active" | "completed",
      "reservation_date": "ISO8601 timestamp",
      "return_deadline": "ISO8601 timestamp"
    }
  ],
  "total_count": integer
}
```

#### Get book's ALL reservations

```
GET /api/reservations/book/{book_id}
```

**Response**
```json
{
  "book_id": "uuid",
  "title": "string",
  "reservations": [
    {
      "reservation_id": "uuid",
      "user_id": "uuid",
      "user_name": "string",
      "status": "active" | "completed",
      "reservation_date": "ISO8601 timestamp",
      "return_deadline": "ISO8601 timestamp"
    }
  ],
  "total_count": integer
}
```

## Error Handling

All error responses follow the same format:

```json
{
  "error": "Error message",
  "status_code": HTTP_STATUS_CODE
}
```

Common status codes include:

* `400` — Invalid input (e.g., malformed UUID, invalid JSON)
* `404` — Resource not found
* `500` — Internal server error

---

## Notes

* All UUIDs are returned as strings.
* All timestamps use ISO8601 format.
* CORS is enabled globally (`*`).
* All endpoints support `OPTIONS` for preflight requests.
