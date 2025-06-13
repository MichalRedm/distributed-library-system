import { useState } from "react";
import "./App.scss";
import User from "./components/User";
import UserList from "./components/UserList";
import BookList from "./components/BookList";

function App() {
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [selectedBookId, setSelectedBookId] = useState<number | null>(null);
  const [tab, setTab] = useState<"users" | "books">("users");

  const handleSelectUserId = (userId: number) => {
    setSelectedUserId(userId);
  };

  const handleSelectBookId = (bookId: number) => {
    setSelectedBookId(bookId);
  };

  return (
    <div className="App">
      <div>
        <div style={{ display: "flex", justifyContent: "center", marginBottom: "20px" }}>
          <button
            className={`tab-button ${tab === "users" ? "active" : ""}`}
            onClick={() => setTab("users")}
          >
            Users
          </button>
          <button
            className={`tab-button ${tab === "books" ? "active" : ""}`}
            onClick={() => setTab("books")}
          >
            Books
          </button>
        </div>
        {tab === "users" && (
          <UserList onSelectUser={handleSelectUserId} />
        )}
        { tab === "books" && (
          <BookList onSelectBook={handleSelectBookId} />
        )}
      </div>
      <div style={{ display: "flex", flexDirection: "column" }}>
        <User id={selectedUserId} />
        {selectedBookId && (
          <div className="book-details">
            <h2>Selected Book ID: {selectedBookId}</h2>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
