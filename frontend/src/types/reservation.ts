/**
 * Represents the status of a reservation.
 */
export type ReservationStatus = "active" | "completed";

/**
 * Defines the structure for a single reservation object.
 * Note: created_at and updated_at are optional as they may not be returned by all reservation list endpoints.
 */
export interface Reservation {
  reservation_id: string;
  user_id: string;
  book_id: string;
  user_name: string;
  book_title: string;
  status: ReservationStatus;
  reservation_date: string; // ISO8601 timestamp (e.g., "2023-10-27T10:00:00Z")
  return_deadline: string; // ISO8601 timestamp
  created_at?: string; // ISO8601 timestamp - Made optional
  updated_at?: string; // ISO8601 timestamp - Made optional
}

/**
 * Request body for creating a new reservation.
 */
export interface CreateReservationRequest {
  user_id: string;
  book_id: string;
}

/**
 * Request body for updating an existing reservation.
 * Properties are optional, allowing for partial updates.
 */
export interface UpdateReservationRequest {
  status?: ReservationStatus;
  return_deadline?: string; // ISO8601 timestamp
}

/**
 * Request body for bulk cancellation of reservations.
 */
export interface CancelReservationsBulkRequest {
  reservation_ids: string[];
}

/**
 * Response structure for the bulk reservation cancellation endpoint.
 */
export interface CancelReservationsBulkResponse {
  message: string;
  cancelled_count: number;
  total_requested: number;
}
