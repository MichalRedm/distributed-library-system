import api from './api';
import type { 
  User, 
  UserListResponse, 
  UserDetails, 
  ActiveReservationsResponse, 
  AllReservationsResponse 
} from '../types/user';

export async function fetchUsers(): Promise<UserListResponse> {
  const response = await api.get<UserListResponse>('/users');
  return response.data;
}

export async function fetchUserById(userId: string): Promise<UserDetails> {
  const response = await api.get<UserDetails>(`/users/${userId}`);
  return response.data;
}

export async function createUser(username: string): Promise<User> {
  const response = await api.post<User>('/users', { username });
  return response.data;
}

export async function fetchActiveReservations(userId: string): Promise<ActiveReservationsResponse> {
  const response = await api.get<ActiveReservationsResponse>(`/users/${userId}/active-reservations`);
  return response.data;
}

export async function fetchAllReservations(userId: string): Promise<AllReservationsResponse> {
  const response = await api.get<AllReservationsResponse>(`/users/${userId}/reservations`);
  return response.data;
}
