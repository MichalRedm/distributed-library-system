import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchUserById } from "../../services/userService";

interface UserProps {
  id: string | null;
}

const User: React.FC<UserProps> = ({ id }) => {
  useEffect(() => {
    if (id) {
      console.log("Loading user with ID:", id);
    }
  }, [id]);

  const { data, error, isLoading } = useQuery({
    queryKey: ["user", id],
    queryFn: () => {
      if (!id) return Promise.reject("No user ID provided");
      return fetchUserById(id);
    },
    enabled: !!id // only run query if id is not null
  });

  if (!id) {
    return <div className="user"><h2>User Profile</h2><p>Please select a user to view their profile.</p></div>;
  }

  if (isLoading) return <p>Loading user...</p>;
  if (error) return <p>Error loading user: {(error as Error).message}</p>;

  return (
    <div className="user">
      <h2>User Profile</h2>
      <p><strong>ID:</strong> {data?.user_id}</p>
      <p><strong>Username:</strong> {data?.username}</p>
      <p><strong>Created At:</strong> {data?.created_at}</p>
      <p><strong>Active Reservations:</strong> {data?.active_reservations_count}</p>
    </div>
  );
};

export default User;
