export interface User {
  user_id: string;
  username: string;
  created_at: string;
}

export interface UserListResponse {
  users: User[];
  total_count: number;
}

export interface UserDetails extends User {
  active_reservations_count: number;
}

export interface ReservationForUser {
  reservation_id: string;
  book_id: string;
  book_title: string;
  reservation_date: string;
  return_deadline: string;
  created_at: string;
}

export interface ActiveReservationsResponse {
  user_id: string;
  username: string;
  active_reservations: ReservationForUser[];
  active_count: number;
}

export interface AllReservationsResponse {
  user_id: string;
  reservations: {
    reservation_id: string;
    book_id: string;
    book_title: string;
    status: string;
    reservation_date: string;
    return_deadline: string;
  }[];
  total_count: number;
}
