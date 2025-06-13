import api from './api';
import type { 
  Book, 
  BookListResponse, 
  BookAvailabilityResponse, 
  BookReservationsResponse 
} from '../types/book';

export async function fetchBooks(availableOnly = false): Promise<BookListResponse> {
  const response = await api.get<BookListResponse>('/books', {
    params: availableOnly ? { available: true } : undefined
  });
  return response.data;
}

export async function fetchBookById(bookId: string): Promise<Book> {
  const response = await api.get<Book>(`/books/${bookId}`);
  return response.data;
}

export async function fetchBookAvailability(bookId: string): Promise<BookAvailabilityResponse> {
  const response = await api.get<BookAvailabilityResponse>(`/books/${bookId}/availability`);
  return response.data;
}

export async function fetchBookReservations(bookId: string): Promise<BookReservationsResponse> {
  const response = await api.get<BookReservationsResponse>(`/reservations/book/${bookId}`);
  return response.data;
}

export async function createBook(title: string): Promise<Book> {
  const response = await api.post<Book>('/books', { title });
  return response.data;
}
