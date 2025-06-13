import { useEffect } from "react";

interface UserProps {
  id: number | null;
}

const User: React.FC<UserProps> = ({ id }) => {
  useEffect(() => {
    console.log("Loading user with ID:", id);
  }, [id]);

  return (
    <div className="user">
      <h2>User Profile</h2>
      {id === null ? (
        <p>Please select a user to view their profile.</p>
      ) : (
        <p>User ID: {id}</p>
      )}
    </div>
  );
};

export default User;
