import { useState } from "react";
import "./App.scss";
import User from "./components/User";
import UserList from "./components/UserList";

function App() {
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);

  const handleSelectUserId = (userId: number) => {
    setSelectedUserId(userId);
  };

  return (
    <div className="App">
      <UserList onSelectUser={handleSelectUserId} />
      <User id={selectedUserId} />
    </div>
  );
}

export default App;
