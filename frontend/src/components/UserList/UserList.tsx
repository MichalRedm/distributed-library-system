import { useQuery } from "@tanstack/react-query";
import "./UserList.scss";
import { fetchUsers } from "../../services/userService";

interface UserListProps {
  onSelectUser: (userId: number) => void;
}

const UserList: React.FC<UserListProps> = ({ onSelectUser }) => {
  const { data: users, error, isLoading } = useQuery({
    queryKey: ["users"],
    queryFn: fetchUsers,
  });

  if (isLoading) return <p>Loading users...</p>;
  if (error) return <p>Error loading users: {error.message}</p>;

  return (
    <div className="user-list">
      <h2>User List</h2>
      <ul className="user-list__items">
        {users?.map(user => (
          <li
            key={user.id}
            className="user-list__item"
            onClick={() => onSelectUser(user.id)}
          >
            {user.name}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default UserList;
