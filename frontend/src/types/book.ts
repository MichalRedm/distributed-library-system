export type BookStatus = 'available' | 'checked_out';

export interface Book {
  book_id: string;
  title: string;
  status: BookStatus;
  created_at: string; // ISO8601 timestamp
}

export interface BookListResponse {
  books: Book[];
  total_count: number;
  filter_applied: 'available_only' | 'none';
}

export interface BookAvailabilityResponse {
  book_id: string;
  available: boolean;
  status: BookStatus;
}

export interface ReservationForBook {
  reservation_id: string;
  user_id: string;
  user_name: string;
  status: string;
  reservation_date: string;
  return_deadline: string;
}

export interface BookReservationsResponse {
  book_id: string;
  reservations: ReservationForBook[];
  total_count: number;
}
