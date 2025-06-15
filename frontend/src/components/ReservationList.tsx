import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateReservation } from "../services/reservationService";
import { formatDate } from "../utils/dateUtils";
import type { Reservation } from "../types/reservation"; // Assuming you have a Reservation type defined

interface ReservationListProps {
  reservations: Reservation[];
  listType: "user" | "book"; // To determine what text to display (e.g., "Book:" vs "User:")
}

const ReservationList: React.FC<ReservationListProps> = ({ reservations, listType }) => {
  const queryClient = useQueryClient();
  const [openReservationId, setOpenReservationId] = useState<string | null>(null);
  const [showModal, setShowModal] = useState<boolean>(false); // State to control modal visibility
  const [reservationToExtend, setReservationToExtend] = useState<Reservation | null>(null); // State to store reservation being extended
  const [newDeadline, setNewDeadline] = useState<string>(''); // State for the new deadline date input

  // Define a mutation for updating a reservation (Mark as Returned or Extend Deadline)
  const updateReservationMutation = useMutation({
    mutationFn: ({ reservationId, data }: { reservationId: string; data: Partial<Reservation>; userId: string; bookId: string; }) =>
      updateReservation(reservationId, data),
    onSuccess: (_, variables) => {
      // Invalidate queries relevant to both the user and the book
      queryClient.invalidateQueries({ queryKey: ["user-reservations", variables.userId] });
      queryClient.invalidateQueries({ queryKey: ["book", variables.bookId] });
      queryClient.invalidateQueries({ queryKey: ["book-reservations", variables.bookId] });
      queryClient.invalidateQueries({ queryKey: ["books"] }); // Invalidate general books list

      setOpenReservationId(null); // Close the accordion after update
      setShowModal(false); // Close the modal if open
      setReservationToExtend(null); // Clear the reservation being extended
      setNewDeadline(''); // Clear the new deadline input
    },
    onError: (error) => {
      console.error("Failed to update reservation:", error);
      // Using alert for simplicity, consider a custom modal for user feedback
      alert("Failed to update reservation. Please try again.");
    },
  });

  const handleReservationClick = (reservationId: string) => {
    setOpenReservationId(prevId => (prevId === reservationId ? null : reservationId));
  };

  const handleMarkAsReturned = (reservationId: string, userId: string, bookId: string) => {
    updateReservationMutation.mutate({ reservationId, data: { status: 'completed' }, userId, bookId });
  };

  const handleExtendDeadlineClick = (reservation: Reservation) => {
    setShowModal(true);
    setReservationToExtend(reservation);
    // Pre-fill with current deadline if available, formatted for date input
    // Ensure it's based on UTC date to avoid timezone shifts for the date picker
    const currentDeadlineDate = reservation.return_deadline ? new Date(reservation.return_deadline) : null;
    let prefilledDate = '';
    if (currentDeadlineDate) {
      prefilledDate = new Date(currentDeadlineDate.getTime() - (currentDeadlineDate.getTimezoneOffset() * 60000))
        .toISOString().split('T')[0];
    }
    setNewDeadline(prefilledDate);
  };

  const handleDeadlineSubmit = () => {
    if (reservationToExtend && newDeadline) {
      // Create a Date object from the YYYY-MM-DD input string
      const date = new Date(newDeadline);
      // Construct a UTC date string to ensure the timestamp consistently refers to midnight UTC of that day
      const newDeadlineISO = new Date(Date.UTC(
        date.getFullYear(),
        date.getMonth(),
        date.getDate()
      )).toISOString();

      updateReservationMutation.mutate({
        reservationId: reservationToExtend.reservation_id,
        data: { return_deadline: newDeadlineISO },
        userId: reservationToExtend.user_id,
        bookId: reservationToExtend.book_id,
      });
    }
  };

  const closeModal = () => {
    setShowModal(false);
    setReservationToExtend(null);
    setNewDeadline('');
  };

  // Sort reservations: active first, then by reservation_date
  const sortedReservations = reservations.slice().sort((a, b) => {
    // Active reservations come before completed ones
    if (a.status === "active" && b.status !== "active") return -1;
    if (a.status !== "active" && b.status === "active") return 1;
    // For same status, sort by reservation_date
    return a.reservation_date.localeCompare(b.reservation_date);
  });

  return (
    <ul className="space-y-3 flex-grow overflow-y-auto pr-2">
      {sortedReservations.length === 0 ? (
        <p className="text-neutral-400 text-center py-4">No reservations found.</p>
      ) : (
        sortedReservations.map(reservation => (
          <li
            key={reservation.reservation_id}
            className={`bg-neutral-600 p-3 rounded-lg shadow-sm cursor-pointer transition-all duration-300 ease-in-out
              ${reservation.status === 'active' ? 'border-l-4 border-green-500 bg-neutral-500 hover:bg-neutral-400' : 'hover:bg-neutral-500'}
              ${openReservationId === reservation.reservation_id ? 'ring-2 ring-blue-500' : ''}
            `}
            onClick={() => handleReservationClick(reservation.reservation_id)}
          >
            <div className="flex justify-between items-center">
              <p className="font-bold text-neutral-200">
                {listType === "user" ? `Book: ${reservation.book_title}` : `User: ${reservation.user_name}`}
              </p>
              <span className={`text-sm font-semibold ${reservation.status === 'active' ? 'text-green-400' : 'text-gray-400'}`}>
                {reservation.status === 'active' ? 'Active' : 'Completed'}
              </span>
            </div>
            {openReservationId === reservation.reservation_id && (
              <div className="mt-2 text-neutral-300 space-y-1 text-sm border-t border-neutral-700 pt-2">
                <p><strong className="text-neutral-300">Reservation Date:</strong> {formatDate(reservation.reservation_date)}</p>
                <p><strong className="text-neutral-300">Return Deadline:</strong> {formatDate(reservation.return_deadline)}</p>

                {reservation.status === 'active' && (
                  <div className="flex flex-wrap gap-2 mt-3"> {/* Use flex-wrap for buttons */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation(); // Prevent accordion from closing when button is clicked
                        handleMarkAsReturned(reservation.reservation_id, reservation.user_id, reservation.book_id);
                      }}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                      disabled={updateReservationMutation.isPending}
                    >
                      {updateReservationMutation.isPending && updateReservationMutation.variables?.data?.status === 'completed' ? "Returning..." : "Mark as Returned"}
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation(); // Prevent accordion from closing when button is clicked
                        handleExtendDeadlineClick(reservation);
                      }}
                      className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                      disabled={updateReservationMutation.isPending}
                    >
                      Extend Deadline
                    </button>
                  </div>
                )}
              </div>
            )}
          </li>
        ))
      )}

      {/* Deadline Extension Modal */}
      {showModal && reservationToExtend && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-neutral-800 p-6 rounded-lg shadow-xl max-w-sm w-full border border-neutral-700">
            <h3 className="text-xl font-semibold mb-4 text-neutral-200">Extend Deadline for &quot;{reservationToExtend.book_title}&quot;</h3>
            <p className="text-neutral-400 mb-4">Current Deadline: {formatDate(reservationToExtend.return_deadline)}</p>

            <label htmlFor="newDeadline" className="block text-neutral-300 text-sm font-medium mb-2">New Return Deadline:</label>
            <input
              type="date"
              id="newDeadline"
              value={newDeadline}
              onChange={(e) => setNewDeadline(e.target.value)}
              className="block w-full p-2 rounded-md bg-neutral-700 text-neutral-200 border border-neutral-600 focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
            />

            <div className="flex justify-end gap-3">
              <button
                onClick={closeModal}
                className="px-4 py-2 bg-neutral-600 text-neutral-200 rounded-md hover:bg-neutral-500 transition-colors duration-200"
              >
                Cancel
              </button>
              <button
                onClick={handleDeadlineSubmit}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!newDeadline || updateReservationMutation.isPending}
              >
                {updateReservationMutation.isPending && updateReservationMutation.variables?.data?.return_deadline ? "Updating..." : "Submit"}
              </button>
            </div>
          </div>
        </div>
      )}
    </ul>
  );
};

export default ReservationList;
