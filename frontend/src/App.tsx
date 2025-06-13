import { useState } from "react";
import "./App.scss";
import User from "./components/User";
import UserList from "./components/UserList";
import BookList from "./components/BookList";
import Book from "./components/Book";
import { createReservation } from "./services/reservationService";
import { fetchBookById } from "./services/bookService"; // Import fetchBookById
import { useQueryClient, useQuery } from "@tanstack/react-query";

function App() {
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [selectedBookId, setSelectedBookId] = useState<string | null>(null);
  const [tab, setTab] = useState<"users" | "books">("users");
  const [isCreatingReservation, setIsCreatingReservation] = useState<boolean>(false);

  const queryClient = useQueryClient();

  // Fetch full book data for the currently selected book to get its status
  const { data: selectedBookData, isLoading: isBookDataLoading } = useQuery({
    queryKey: ["book", selectedBookId], // Use the same query key as the Book component
    queryFn: () => {
      if (!selectedBookId) return Promise.reject("No book ID provided");
      return fetchBookById(selectedBookId);
    },
    enabled: !!selectedBookId, // Only run this query if a book is selected
  });

  const handleSelectUserId = (userId: string) => {
    setSelectedUserId(userId);
  };

  const handleSelectBookId = (bookId: string) => {
    setSelectedBookId(bookId);
  };

  /**
   * Handles the creation of a new reservation when the button is clicked.
   */
  const handleCreateReservation = async () => {
    if (selectedUserId && selectedBookId) {
      setIsCreatingReservation(true);
      try {
        await createReservation({
          user_id: selectedUserId,
          book_id: selectedBookId,
        });

        // Invalidate queries to trigger re-fetches for relevant data
        queryClient.invalidateQueries({ queryKey: ["user-reservations", selectedUserId] }); // Update user's reservations
        queryClient.invalidateQueries({ queryKey: ["book", selectedBookId] }); // Update book status in Book component and selectedBookData here
        queryClient.invalidateQueries({ queryKey: ["books"] }); // Update book list if filtering by availability
      } catch (error) {
        console.error("Failed to create reservation:", error);
        alert("Failed to create reservation. Please try again.");
      } finally {
        setIsCreatingReservation(false);
      }
    }
  };

  // Determine if the checkout button should be disabled
  const isCheckoutDisabled =
    !selectedUserId ||
    !selectedBookId ||
    isCreatingReservation ||
    isBookDataLoading || // Disable if book data is still loading
    (selectedBookData?.status === 'checked_out'); // Disable if the selected book is checked out


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
                }}
              >
                Users
              </button>
              <button
                className={`tab-button px-6 py-3 rounded-lg text-lg font-medium transition-colors duration-200
                  ${tab === "books" ? "bg-blue-600 text-white shadow-md" : "bg-neutral-600 text-neutral-300 hover:bg-neutral-500"}`}
                onClick={() => {
                  setTab("books");
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
            <User id={selectedUserId} />

            {/* Selected Book Details */}
            <Book id={selectedBookId} />

            {/* Create Reservation Section */}
            <div className="bg-neutral-800 shadow-lg rounded-lg p-6 flex flex-col items-center">
              <h2 className="text-xl font-semibold mb-4 text-neutral-200">Create New Reservation</h2>
              <button
                className={`px-8 py-4 rounded-xl text-xl font-bold transition-all duration-300 ease-in-out
                  ${!isCheckoutDisabled
                    ? "bg-green-600 text-white hover:bg-green-700 shadow-lg transform hover:scale-105"
                    : "bg-neutral-600 text-neutral-400 cursor-not-allowed"
                  }`}
                onClick={handleCreateReservation}
                disabled={isCheckoutDisabled}
              >
                {isCreatingReservation
                  ? "Checking out..."
                  : selectedBookData?.status === 'checked_out' && selectedBookId // Check status from selectedBookData
                  ? "Book Not Available"
                  : "Check out"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
