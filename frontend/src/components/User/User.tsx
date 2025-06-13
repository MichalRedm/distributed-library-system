import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchUserById, fetchAllReservations } from "../../services/userService";
import "./User.scss"; // we'll use it in a moment

interface UserProps {
  id: string | null;
}

const User: React.FC<UserProps> = ({ id }) => {
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

  if (!id) {
    return <div className="user"><h2>User Profile</h2><p>Please select a user to view their profile.</p></div>;
  }

  if (userLoading || reservationsLoading) return <p>Loading user...</p>;
  if (userError) return <p>Error loading user: {(userError as Error).message}</p>;
  if (reservationsError) return <p>Error loading reservations: {(reservationsError as Error).message}</p>;
  if (!reservationsData) return null;

  // Sort reservations by reservation_date
  const sortedReservations = reservationsData.reservations.slice().sort((a, b) =>
    a.reservation_date.localeCompare(b.reservation_date)
  );

  return (
    <div className="user">
      <h2>User Profile</h2>
      <p><strong>Username:</strong> {user?.username}</p>
      <p><strong>Created At:</strong> {user?.created_at}</p>

      <h3>Reservations</h3>
      {sortedReservations.length === 0 ? (
        <p>No reservations found.</p>
      ) : (
        <ul className="list-items">
          {sortedReservations.map(reservation => (
            <li key={reservation.reservation_id} className="list-item">
              <p><strong>Book:</strong> {reservation.book_title}</p>
              <p><strong>Status:</strong> {reservation.status}</p>
              <p><strong>Reservation Date:</strong> {reservation.reservation_date}</p>
              <p><strong>Return Deadline:</strong> {reservation.return_deadline}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default User;
