import { useQuery } from "@tanstack/react-query";
import { fetchUsers } from "../../services/userService";
import SelectableList from "../SelectableList/SelectableList";
import type { User } from "../../types/user";

interface UserListProps {
  onSelectUser: (userId: string) => void;
}

const UserList: React.FC<UserListProps> = ({ onSelectUser }) => {
  const { data, error, isLoading } = useQuery({
    queryKey: ["users"],
    queryFn: fetchUsers,
  });

  const users = data?.users ?? [];

  return (
    <div>
      <h2>Users</h2>
      <SelectableList<User>
        data={users}
        isLoading={isLoading}
        error={error}
        extractId={(user) => user.user_id}
        extractLabel={(user) => user.username}
        onSelect={onSelectUser}
        searchPlaceholder="Search users..."
      />
    </div>
  );
};

export default UserList;
