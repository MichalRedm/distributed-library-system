import api from './api';
import type {
  Reservation,
  CreateReservationRequest,
  UpdateReservationRequest,
  CancelReservationsBulkRequest,
  CancelReservationsBulkResponse,
} from '../types/reservation';

/**
 * Makes a new reservation for a book by a user.
 * @param data - An object containing `user_id` and `book_id`.
 * @returns A Promise that resolves to the newly created Reservation object.
 */
export async function createReservation(data: CreateReservationRequest): Promise<Reservation> {
  const response = await api.post<Reservation>('/reservations', data);
  return response.data;
}

/**
 * Fetches a specific reservation by its ID.
 * @param reservationId - The UUID of the reservation to fetch.
 * @returns A Promise that resolves to the Reservation object.
 */
export async function fetchReservationById(reservationId: string): Promise<Reservation> {
  const response = await api.get<Reservation>(`/reservations/${reservationId}`);
  return response.data;
}

/**
 * Updates an existing reservation.
 * @param reservationId - The UUID of the reservation to update.
 * @param data - An object containing the fields to update (e.g., `status`, `return_deadline`).
 * @returns A Promise that resolves to the updated Reservation object.
 */
export async function updateReservation(reservationId: string, data: UpdateReservationRequest): Promise<Reservation> {
  const response = await api.put<Reservation>(`/reservations/${reservationId}`, data);
  return response.data;
}

/**
 * Cancels multiple reservations in a single request.
 * @param data - An object containing an array of `reservation_ids` to cancel.
 * @returns A Promise that resolves to a CancelReservationsBulkResponse object,
 * indicating the number of reservations cancelled.
 */
export async function cancelReservationsBulk(data: CancelReservationsBulkRequest): Promise<CancelReservationsBulkResponse> {
  // For DELETE requests with a body, Axios requires the body to be passed via the 'data' property
  const response = await api.delete<CancelReservationsBulkResponse>('/reservations/bulk', { data });
  return response.data;
}
