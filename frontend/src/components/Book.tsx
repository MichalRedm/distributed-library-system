import { useEffect, useState } from "react";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query"; // Import useMutation
import { fetchBookById, fetchBookReservations } from "../services/bookService";
import { updateReservation } from "../services/reservationService"; // Import updateReservation
import { formatDate } from "../utils/dateUtils";

// Import Font Awesome React components and icons
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBook, faBookOpen } from '@fortawesome/free-solid-svg-icons';

interface BookProps {
  id: string | null;
}

const Book: React.FC<BookProps> = ({ id }) => {
  const queryClient = useQueryClient();
  const [openReservationId, setOpenReservationId] = useState<string | null>(null);

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

  // Define a mutation for updating a reservation
  const updateReservationMutation = useMutation({
    mutationFn: ({ reservationId }: { reservationId: string; userId: string }) =>
      updateReservation(reservationId, { status: 'completed' }),
    onSuccess: (_, variables) => {
      // Invalidate the 'book' query for the current book ID to update its status
      queryClient.invalidateQueries({ queryKey: ["book", id] });
      // Invalidate the 'book-reservations' query for the current book ID to update the list
      queryClient.invalidateQueries({ queryKey: ["book-reservations", id] });
      // Invalidate the 'user-reservations' query for the specific user who had the reservation
      queryClient.invalidateQueries({ queryKey: ["user-reservations", variables.userId] });

      setOpenReservationId(null); // Close the accordion after update
    },
    onError: (error) => {
      console.error("Failed to update reservation:", error);
      alert("Failed to update reservation. Please try again."); // Using alert for simplicity, consider a custom modal
    },
  });

  const handleReservationClick = (reservationId: string) => {
    setOpenReservationId(prevId => (prevId === reservationId ? null : reservationId));
  };

  const handleMarkAsReturned = (reservationId: string, userId: string) => {
    updateReservationMutation.mutate({ reservationId, userId });
  };


  if (!id) {
    return (
      <div className="p-4 bg-neutral-700 rounded-lg text-neutral-400 text-center min-h-full">
        <FontAwesomeIcon icon={faBook} className="text-5xl mb-3 text-neutral-500" /> {/* Book Icon */}
        <p className="text-xl font-semibold mb-2 text-neutral-200">Select a book</p>
        <p>Please select a book to view its details.</p>
      </div>
    );
  }

  if (bookLoading || reservationsLoading) return <p className="text-neutral-400 text-center py-4">Loading book details and reservations...</p>;
  if (bookError) return <p className="text-red-500 text-center py-4">Error loading book: {(bookError as Error).message}</p>;
  if (reservationsError) return <p className="text-red-500 text-center py-4">Error loading reservations: {(reservationsError as Error).message}</p>;
  if (!reservationsData || !bookData) return null;

  // Sort reservations: active first, then by reservation_date
  const sortedReservations = reservationsData.reservations.slice().sort((a, b) => {
    // Active reservations come before completed ones
    if (a.status === "active" && b.status !== "active") return -1;
    if (a.status !== "active" && b.status === "active") return 1;
    // For same status, sort by reservation_date
    return a.reservation_date.localeCompare(b.reservation_date);
  });

  return (
    <div className="book p-4 bg-neutral-700 rounded-lg shadow-inner min-h-full">
      <div className="flex items-center mb-4">
        <FontAwesomeIcon icon={faBookOpen} className="text-5xl mr-4 text-neutral-400" /> {/* Book Icon */}
        <h2 className="text-3xl font-bold text-neutral-100">{bookData?.title}</h2> {/* Book title as heading */}
      </div>

      <p className="mb-1"><strong className="text-neutral-300">Status:</strong> <span className={`${bookData?.status === 'available' ? 'text-green-400' : 'text-orange-400'}`}>{bookData?.status}</span></p>
      <p><strong className="text-neutral-300">Created At:</strong> {formatDate(bookData?.created_at)}</p>

      <h3 className="text-xl font-semibold mb-3 text-neutral-200 border-b border-neutral-600 pb-2 mt-6">Reservations for this Book</h3>
      {sortedReservations.length === 0 ? (
        <p className="text-neutral-400">No reservations found for this book.</p>
      ) : (
        <ul className="space-y-3">
          {sortedReservations.map(reservation => (
            <li
              key={reservation.reservation_id}
              className={`bg-neutral-600 p-3 rounded-lg shadow-sm cursor-pointer transition-all duration-300 ease-in-out
                ${reservation.status === 'active' ? 'border-l-4 border-green-500 bg-neutral-500 hover:bg-neutral-400' : 'hover:bg-neutral-500'}
                ${openReservationId === reservation.reservation_id ? 'ring-2 ring-blue-500' : ''}
              `}
              onClick={() => handleReservationClick(reservation.reservation_id)}
            >
              <div className="flex justify-between items-center">
                <p className="font-bold text-neutral-200">User: {reservation.user_name}</p>
                <span className={`text-sm font-semibold ${reservation.status === 'active' ? 'text-green-400' : 'text-gray-400'}`}>
                  {reservation.status === 'active' ? 'Active' : 'Completed'}
                </span>
              </div>
              {openReservationId === reservation.reservation_id && (
                <div className="mt-2 text-neutral-300 space-y-1 text-sm border-t border-neutral-700 pt-2">
                  <p><strong className="text-neutral-300">Reservation Date:</strong> {formatDate(reservation.reservation_date)}</p>
                  <p><strong className="text-neutral-300">Return Deadline:</strong> {formatDate(reservation.return_deadline)}</p>

                  {reservation.status === 'active' && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation(); // Prevent accordion from closing when button is clicked
                        handleMarkAsReturned(reservation.reservation_id, reservation.user_id);
                      }}
                      className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                      disabled={updateReservationMutation.isPending}
                    >
                      {updateReservationMutation.isPending ? "Returning..." : "Mark as Returned"}
                    </button>
                  )}
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Book;
