import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchUserById, fetchAllReservations } from "../services/userService";
import { formatDate } from "../utils/dateUtils";

// Import Font Awesome React components and icons
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faUserCircle } from '@fortawesome/free-solid-svg-icons';

import ReservationList from "./ReservationList"; // Import the new component
import type { Reservation, ReservationStatus } from "../types/reservation";

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
    return (
      <div className="p-4 bg-neutral-700 shadow-lg rounded-lg text-neutral-400 text-center min-h-full flex flex-col items-center justify-center">
        <FontAwesomeIcon icon={faUser} className="text-5xl mb-3 text-neutral-500" />
        <p className="text-xl font-semibold mb-2 text-neutral-200">Select a user</p>
        <p>Please select a user to view their profile.</p>
      </div>
    );
  }

  if (userLoading || reservationsLoading) return <p className="text-neutral-400 text-center py-4 h-full flex items-center justify-center">Loading user...</p>;
  if (userError) return <p className="text-red-500 text-center py-4 h-full flex items-center justify-center">Error loading user: {(userError as Error).message}</p>;
  if (reservationsError) return <p className="text-red-500 text-center py-4 h-full flex items-center justify-center">Error loading reservations: {(reservationsError as Error).message}</p>;
  if (!reservationsData) return null;

  // Transform reservations to match the full Reservation interface expected by ReservationList
  // This adds user_id and user_name which are available from the top-level user object but not in each nested reservation from the API response
  // Explicitly cast 'status' to 'ReservationStatus' to resolve type mismatch
  const transformedReservations: Reservation[] = reservationsData.reservations.map(res => ({
    ...res,
    user_id: user ? user.user_id : '', // Add user_id from the fetched user data
    user_name: user ? user.username : '', // Add username from the fetched user data
    status: res.status as ReservationStatus, // Cast status to the correct type
  }));

  return (
    <div className="user p-4 bg-neutral-700 rounded-lg shadow-inner min-h-full flex flex-col">
      <div className="flex items-center mb-4 flex-shrink-0">
        <FontAwesomeIcon icon={faUserCircle} className="text-5xl mr-4 text-neutral-400" />
        <h2 className="text-3xl font-bold text-neutral-100">{user?.username}</h2>
      </div>

      <p className="mb-3 text-neutral-400 text-sm flex-shrink-0"><strong className="text-neutral-300">Member Since:</strong> {formatDate(user?.created_at)}</p>

      <h3 className="text-xl font-semibold mb-3 text-neutral-200 border-b border-neutral-600 pb-2 flex-shrink-0">Reservations</h3>
      {/* Pass the transformed reservations to ReservationList */}
      <ReservationList reservations={transformedReservations} listType="user" />
    </div>
  );
};

export default User;

