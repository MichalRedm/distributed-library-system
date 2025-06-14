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

  // Define a mutation for updating a reservation
  const updateReservationMutation = useMutation({
    mutationFn: ({ reservationId }: { reservationId: string; userId: string }) =>
      updateReservation(reservationId, { status: 'completed' }),
    onSuccess: (data, variables) => {
      // Invalidate queries relevant to both the user and the book
      queryClient.invalidateQueries({ queryKey: ["user-reservations", variables.userId] });
      queryClient.invalidateQueries({ queryKey: ["book", data.book_id] });
      queryClient.invalidateQueries({ queryKey: ["book-reservations", data.book_id] });
      queryClient.invalidateQueries({ queryKey: ["books"] }); // Invalidate general books list

      setOpenReservationId(null); // Close the accordion after update
    },
    onError: (error) => {
      console.error("Failed to update reservation:", error);
      alert("Failed to update reservation. Please try again.");
    },
  });

  const handleReservationClick = (reservationId: string) => {
    setOpenReservationId(prevId => (prevId === reservationId ? null : reservationId));
  };

  const handleMarkAsReturned = (reservationId: string, userId: string) => {
    updateReservationMutation.mutate({ reservationId, userId });
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
        ))
      )}
    </ul>
  );
};

export default ReservationList;
