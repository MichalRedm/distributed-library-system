import { useEffect, useState } from "react"; // Import useState
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchUserById, fetchAllReservations } from "../../services/userService";
import { formatDate } from "../../utils/dateUtils";

interface UserProps {
  id: string | null;
}

const User: React.FC<UserProps> = ({ id }) => {
  const queryClient = useQueryClient();
  const [openReservationId, setOpenReservationId] = useState<string | null>(null); // State to manage open accordion item

  useEffect(() => {
    if (id) {
      console.log("Loading user with ID:", id);
    }
  }, [id]);

  const { data: user, error: userError, isLoading: userLoading } = useQuery({
    queryKey: ["user", id],
    queryFn: () => {
      if (!id) return Promise.reject("No user ID provided");
      return fetchUserById(id);
    },
    enabled: !!id
  });

  const { data: reservationsData, error: reservationsError, isLoading: reservationsLoading } = useQuery({
    queryKey: ["user-reservations", id],
    queryFn: () => {
      if (!id) return Promise.reject("No user ID provided");
      return fetchAllReservations(id);
    },
    enabled: !!id
  });

  // Effect to invalidate and refetch user reservations when a new reservation is created
  useEffect(() => {
    if (id) {
      queryClient.invalidateQueries({ queryKey: ["user-reservations", id] });
    }
  }, [id, queryClient]);

  const handleReservationClick = (reservationId: string) => {
    setOpenReservationId(prevId => (prevId === reservationId ? null : reservationId));
  };

  if (!id) {
    return (
      <div className="p-4 bg-neutral-700 rounded-lg text-neutral-400">
        <h2 className="text-xl font-semibold mb-2 text-neutral-200">User Profile</h2>
        <p>Please select a user to view their profile.</p>
      </div>
    );
  }

  if (userLoading || reservationsLoading) return <p className="text-neutral-400">Loading user...</p>;
  if (userError) return <p className="text-red-500">Error loading user: {(userError as Error).message}</p>;
  if (reservationsError) return <p className="text-red-500">Error loading reservations: {(reservationsError as Error).message}</p>;
  if (!reservationsData) return null;

  // Sort reservations: active first, then by reservation_date
  const sortedReservations = reservationsData.reservations.slice().sort((a, b) => {
    // Active reservations come before completed ones
    if (a.status === "active" && b.status !== "active") return -1;
    if (a.status !== "active" && b.status === "active") return 1;
    // For same status, sort by reservation_date
    return a.reservation_date.localeCompare(b.reservation_date);
  });

  return (
    <div className="user p-4 bg-neutral-700 rounded-lg shadow-inner">
      <h2 className="text-xl font-semibold mb-3 text-neutral-200">User Profile</h2>
      <p className="mb-1"><strong className="text-neutral-300">Username:</strong> {user?.username}</p>
      <p className="mb-3"><strong className="text-neutral-300">Created At:</strong> {formatDate(user?.created_at)}</p>

      <h3 className="text-lg font-semibold mb-2 text-neutral-200">Reservations</h3>
      {sortedReservations.length === 0 ? (
        <p className="text-neutral-400">No reservations found.</p>
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
                <p className="font-bold text-neutral-200">Book: {reservation.book_title}</p>
                <span className={`text-sm font-semibold ${reservation.status === 'active' ? 'text-green-400' : 'text-gray-400'}`}>
                  {reservation.status === 'active' ? 'Active' : 'Completed'}
                </span>
              </div>
              {openReservationId === reservation.reservation_id && (
                <div className="mt-2 text-neutral-300 space-y-1 text-sm">
                  <p><strong className="text-neutral-300">Reservation Date:</strong> {formatDate(reservation.reservation_date)}</p>
                  <p><strong className="text-neutral-300">Return Deadline:</strong> {formatDate(reservation.return_deadline)}</p>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default User;
