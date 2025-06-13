import { useQuery } from "@tanstack/react-query";
import { fetchUsers } from "../../services/userService";
import SelectableList from "../SelectableList/SelectableList";
import type { User } from "../../types/user";

interface UserListProps {
  selectedUserId: string | null;
  onSelectUser: (userId: string) => void;
}

const UserList: React.FC<UserListProps> = ({ selectedUserId, onSelectUser }) => {
  const { data, error, isLoading } = useQuery({
    queryKey: ["users"],
    queryFn: fetchUsers,
  });

  const users = data?.users ?? [];

  return (
    <div>
      <SelectableList<User>
        data={users}
        isLoading={isLoading}
        error={error}
        extractId={(user) => user.user_id}
        extractLabel={(user) => user.username}
        onSelect={onSelectUser}
        searchPlaceholder="Search users..."
        selectedId={selectedUserId}
      />
    </div>
  );
};

export default UserList;
