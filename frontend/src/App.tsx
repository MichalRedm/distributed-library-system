import { useState } from "react";
import "./App.scss";
import User from "./components/User";
import UserList from "./components/UserList";
import BookList from "./components/BookList";
import Book from "./components/Book";
import { createReservation } from "./services/reservationService"; // Import the createReservation function
import { useQueryClient } from "@tanstack/react-query"; // Import useQueryClient

function App() {
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [selectedBookId, setSelectedBookId] = useState<string | null>(null);
  const [tab, setTab] = useState<"users" | "books">("users");
  const [isCreatingReservation, setIsCreatingReservation] = useState<boolean>(false);
  const [reservationMessage, setReservationMessage] = useState<string | null>(null);
  const [isError, setIsError] = useState<boolean>(false);

  const queryClient = useQueryClient(); // Initialize useQueryClient

  const handleSelectUserId = (userId: string) => {
    setSelectedUserId(userId);
    // Reset messages when a new user is selected
    setReservationMessage(null);
    setIsError(false);
  };

  const handleSelectBookId = (bookId: string) => {
    setSelectedBookId(bookId);
    // Reset messages when a new book is selected
    setReservationMessage(null);
    setIsError(false);
  };

  /**
   * Handles the creation of a new reservation when the button is clicked.
   */
  const handleCreateReservation = async () => {
    if (selectedUserId && selectedBookId) {
      setIsCreatingReservation(true);
      setReservationMessage(null);
      setIsError(false);
      try {
        const reservation = await createReservation({
          user_id: selectedUserId,
          book_id: selectedBookId,
        });
        setReservationMessage(`Reservation created successfully! ID: ${reservation.reservation_id}`);
        setIsError(false);

        // Invalidate the specific user's reservations query
        // This will cause the User component to refetch its reservations
        queryClient.invalidateQueries({ queryKey: ["user-reservations", selectedUserId] });

        // Do NOT reset selected user/book here, as requested
        // setSelectedUserId(null);
        // setSelectedBookId(null);
      } catch (error) {
        console.error("Failed to create reservation:", error);
        setReservationMessage("Failed to create reservation. Please try again.");
        setIsError(true);
      } finally {
        setIsCreatingReservation(false);
      }
    }
  };

  return (
    <div className="App flex flex-col items-center p-4 min-h-screen bg-neutral-900 font-sans text-neutral-300">
      <div className="w-full max-w-4xl bg-neutral-800 shadow-lg rounded-lg p-6 mb-8">
        {/* Main Content Area: Two Columns */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Left Column: Tab Navigation and User or Book List */}
          <div className="bg-neutral-700 p-4 rounded-lg shadow-inner flex flex-col">
            {/* Tab Navigation moved here */}
            <div className="flex justify-center mb-6 space-x-4">
              <button
                className={`tab-button px-6 py-3 rounded-lg text-lg font-medium transition-colors duration-200
                  ${tab === "users" ? "bg-blue-600 text-white shadow-md" : "bg-neutral-600 text-neutral-300 hover:bg-neutral-500"}`}
                onClick={() => {
                  setTab("users");
                  setReservationMessage(null);
                  setIsError(false);
                }}
              >
                Users
              </button>
              <button
                className={`tab-button px-6 py-3 rounded-lg text-lg font-medium transition-colors duration-200
                  ${tab === "books" ? "bg-blue-600 text-white shadow-md" : "bg-neutral-600 text-neutral-300 hover:bg-neutral-500"}`}
                onClick={() => {
                  setTab("books");
                  setReservationMessage(null);
                  setIsError(false);
                }}
              >
                Books
              </button>
            </div>

            {/* User or Book List */}
            {tab === "users" && (
              <UserList onSelectUser={handleSelectUserId} selectedUserId={selectedUserId} />
            )}
            {tab === "books" && (
              <BookList onSelectBook={handleSelectBookId} selectedBookId={selectedBookId} />
            )}
          </div>

          {/* Right Column: Selected User/Book Details and Create Reservation */}
          <div className="flex flex-col gap-6">
            {/* Selected User Details */}
            <div className="bg-neutral-800 shadow-lg rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3 text-neutral-200">Selected User:</h2>
              <User id={selectedUserId} />
            </div>

            {/* Selected Book Details */}
            <div className="bg-neutral-800 shadow-lg rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3 text-neutral-200">Selected Book:</h2>
              <Book id={selectedBookId} />
            </div>

            {/* Create Reservation Section */}
            <div className="bg-neutral-800 shadow-lg rounded-lg p-6 flex flex-col items-center">
              <button
                className={`px-8 py-4 rounded-xl text-xl font-bold transition-all duration-300 ease-in-out
                  ${selectedUserId && selectedBookId && !isCreatingReservation
                    ? "bg-green-600 text-white hover:bg-green-700 shadow-lg transform hover:scale-105"
                    : "bg-neutral-600 text-neutral-400 cursor-not-allowed"
                  }`}
                onClick={handleCreateReservation}
                disabled={!selectedUserId || !selectedBookId || isCreatingReservation}
              >
                {isCreatingReservation ? "Creating Reservation..." : "Create Reservation"}
              </button>

              {reservationMessage && (
                <p className={`mt-4 text-center text-lg ${isError ? "text-red-600" : "text-green-600"}`}>
                  {reservationMessage}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
