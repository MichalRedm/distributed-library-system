import { useQuery } from "@tanstack/react-query";
import "./UserList.scss";
import { fetchUsers } from "../../services/userService";
import { useState } from "react";

interface UserListProps {
  onSelectUser: (userId: number) => void;
}

const UserList: React.FC<UserListProps> = ({ onSelectUser }) => {
  const { data: users, error, isLoading } = useQuery({
    queryKey: ["users"],
    queryFn: fetchUsers,
  });
  const [searchInput, setSearchInput] = useState("");

  if (isLoading) return <p>Loading users...</p>;
  if (error) return <p>Error loading users: {error.message}</p>;

  const filteredUsers = users?.filter(user =>
    user.username.toLowerCase().includes(searchInput.toLowerCase())
  ) || [];

  return (
    <div className="user-list">
      <h2>Users</h2>
      <input
        type="text"
        placeholder="Search users..."
        value={searchInput}
        onChange={e => setSearchInput(e.target.value)}
        className="user-list__search"
        style={{ marginBottom: "20px" }}
      />
      <ul className="user-list__items">
        {filteredUsers.map(user => (
          <li
            key={user.id}
            className="user-list__item"
            onClick={() => onSelectUser(user.id)}
          >
            {user.username}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default UserList;
