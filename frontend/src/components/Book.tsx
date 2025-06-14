import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchBookById, fetchBookReservations } from "../services/bookService";
import { formatDate } from "../utils/dateUtils";

// Import Font Awesome React components and icons
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBook, faBookOpen } from '@fortawesome/free-solid-svg-icons';

import ReservationList from "./ReservationList"; // Import the new component
import type { Reservation, ReservationStatus } from "../types/reservation"; // Import the Reservation and ReservationStatus types

interface BookProps {
  id: string | null;
}

const Book: React.FC<BookProps> = ({ id }) => {
  useEffect(() => {
    if (id) {
      console.log("Loading book with ID:", id);
    }
  }, [id]);

  const { data: bookData, error: bookError, isLoading: bookLoading } = useQuery({
    queryKey: ["book", id],
    queryFn: () => {
      if (!id) return Promise.reject("No book ID provided");
      return fetchBookById(id);
    },
    enabled: !!id
  });

  const { data: reservationsData, error: reservationsError, isLoading: reservationsLoading } = useQuery({
    queryKey: ["book-reservations", id],
    queryFn: () => {
      if (!id) return Promise.reject("No book ID provided");
      return fetchBookReservations(id);
    },
    enabled: !!id
  });


  if (!id) {
    return (
      <div className="p-4 bg-neutral-700 shadow-lg rounded-lg text-neutral-400 text-center min-h-full flex flex-col items-center justify-center">
        <FontAwesomeIcon icon={faBook} className="text-5xl mb-3 text-neutral-500" />
        <p className="text-xl font-semibold mb-2 text-neutral-200">Select a book</p>
        <p>Please select a book to view its details.</p>
      </div>
    );
  }

  if (bookLoading || reservationsLoading) return <p className="text-neutral-400 text-center py-4 h-full flex items-center justify-center">Loading book details and reservations...</p>;
  if (bookError) return <p className="text-red-500 text-center py-4 h-full flex items-center justify-center">Error loading book: {(bookError as Error).message}</p>;
  if (reservationsError) return <p className="text-red-500 text-center py-4 h-full flex items-center justify-center">Error loading reservations: {(reservationsError as Error).message}</p>;
  if (!reservationsData || !bookData) return null;

  // Transform reservations to match the full Reservation interface expected by ReservationList
  // Add book_id and book_title from the component's props and fetched bookData
  const transformedReservations: Reservation[] = reservationsData.reservations.map(res => ({
    ...res,
    book_id: id || '', // Use the id prop for book_id
    book_title: bookData ? bookData.title : '', // Use the fetched bookData.title for book_title
    user_id: res.user_id,
    user_name: res.user_name,
    status: res.status as ReservationStatus, // Cast status to the correct type
  }));

  return (
    <div className="book p-4 bg-neutral-700 rounded-lg shadow-inner min-h-full flex flex-col">
      <div className="flex items-center mb-4 flex-shrink-0">
        <FontAwesomeIcon icon={faBookOpen} className="text-5xl mr-4 text-neutral-400" />
        <h2 className="text-3xl font-bold text-neutral-100">{bookData?.title}</h2>
      </div>

      <p className="mb-1 flex-shrink-0"><strong className="text-neutral-300">Status:</strong> <span className={`${bookData?.status === 'available' ? 'text-green-400' : 'text-orange-400'}`}>{bookData?.status}</span></p>
      <p className="flex-shrink-0"><strong className="text-neutral-300">Created At:</strong> {formatDate(bookData?.created_at)}</p>

      <h3 className="text-xl font-semibold mb-3 text-neutral-200 border-b border-neutral-600 pb-2 mt-6 flex-shrink-0">Reservations for this Book</h3>
      {/* Pass the transformed reservations to ReservationList */}
      <ReservationList reservations={transformedReservations} listType="book" />
    </div>
  );
};

export default Book;
