import { useState } from "react";
import "./App.scss";
import User from "./components/User";
import UserList from "./components/UserList";
import BookList from "./components/BookList";
import Book from "./components/Book";

function App() {
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [selectedBookId, setSelectedBookId] = useState<string | null>(null);
  const [tab, setTab] = useState<"users" | "books">("users");

  const handleSelectUserId = (userId: string) => {
    setSelectedUserId(userId);
  };

  const handleSelectBookId = (bookId: string) => {
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
        {tab === "books" && (
          <BookList onSelectBook={handleSelectBookId} />
        )}
      </div>
      <div style={{ display: "flex", flexDirection: "column" }}>
        <User id={selectedUserId} />
        <Book id={selectedBookId} />
      </div>
    </div>
  );
}

export default App;
