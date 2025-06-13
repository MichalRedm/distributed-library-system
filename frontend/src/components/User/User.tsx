import { useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query"; // Import useQueryClient
import { fetchUserById, fetchAllReservations } from "../../services/userService";
// Removed "./User.scss" as we are now using Tailwind CSS
import { formatDate } from "../../utils/dateUtils";

interface UserProps {
  id: string | null;
}

const User: React.FC<UserProps> = ({ id }) => {
  const queryClient = useQueryClient(); // Initialize useQueryClient

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
  // This will be triggered by a direct invalidation from the App.tsx component
  useEffect(() => {
    if (id) {
      // Invalidate the 'user-reservations' query for the current user ID
      // This ensures that when a reservation is successfully created,
      // this component's reservations data is refetched.
      queryClient.invalidateQueries({ queryKey: ["user-reservations", id] });
    }
  }, [id, queryClient]); // Depend on id and queryClient


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

  const sortedReservations = reservationsData.reservations.slice().sort((a, b) =>
    a.reservation_date.localeCompare(b.reservation_date)
  );

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
            <li key={reservation.reservation_id} className="bg-neutral-600 p-3 rounded-lg shadow-sm">
              <p className="mb-1"><strong className="text-neutral-300">Book:</strong> {reservation.book_title}</p>
              <p className="mb-1"><strong className="text-neutral-300">Status:</strong> <span className={`${reservation.status === 'active' ? 'text-green-400' : 'text-gray-400'}`}>{reservation.status}</span></p>
              <p className="mb-1"><strong className="text-neutral-300">Reservation Date:</strong> {formatDate(reservation.reservation_date)}</p>
              <p><strong className="text-neutral-300">Return Deadline:</strong> {formatDate(reservation.return_deadline)}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default User;
