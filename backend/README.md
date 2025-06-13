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

#### Get all reservations for a user

```
GET /api/users/{user_id}/reservations
```

**Response**

```json
{
  "user_id": "uuid",
  "reservations": [
    {
      "reservation_id": "uuid",
      "book_id": "uuid",
      "book_title": "string",
      "status": "string",
      "reservation_date": "ISO8601 timestamp",
      "return_deadline": "ISO8601 timestamp"
    }
  ],
  "total_count": integer
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

#### Get all reservations for a book

```
GET /api/books/{book_id}/reservations
```

**Response**

```json
{
  "book_id": "uuid",
  "reservations": [
    {
      "reservation_id": "uuid",
      "user_id": "uuid",
      "user_name": "string",
      "status": "string",
      "reservation_date": "ISO8601 timestamp",
      "return_deadline": "ISO8601 timestamp"
    }
  ],
  "total_count": integer
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

---

## Future Improvements (Planned)

* Reservation creation and cancellation endpoints
* Pagination and filtering for large datasets
* User authentication and authorization
* Improved validation and error responses
