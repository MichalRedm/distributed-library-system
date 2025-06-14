import { useState } from "react";
import "./App.scss";
import User from "./components/User";
import UserList from "./components/UserList";
import BookList from "./components/BookList";
import Book from "./components/Book";
import { createReservation } from "./services/reservationService";
import { fetchBookById } from "./services/bookService";
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
    // App will take 100% width of the viewport (with margins)
    <div className="App flex flex-col items-center px-4 py-8 min-h-screen bg-neutral-900 font-sans text-neutral-300">
      {/* Main container, now stretching */}
      <div className="w-full max-w-7xl bg-neutral-800 shadow-lg rounded-lg p-6 flex flex-col flex-grow">
        {/* Main Content Area: Two Columns, now stretching */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 flex-grow">
          {/* Left Column: Tab Navigation and User or Book List */}
          <div className="bg-neutral-700 p-4 rounded-lg shadow-inner flex flex-col h-full">
            {/* Tab Navigation */}
            <div className="flex justify-center mb-6 space-x-4 flex-shrink-0">
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

            {/* User or Book List - Stretched to remaining space */}
            <div className="flex-grow overflow-y-auto">
              {tab === "users" && (
                <UserList onSelectUser={handleSelectUserId} selectedUserId={selectedUserId} />
              )}
              {tab === "books" && (
                <BookList onSelectBook={handleSelectBookId} selectedBookId={selectedBookId} />
              )}
            </div>
          </div>

          {/* Right Column: Selected User/Book Details and Create Reservation */}
          <div className="flex flex-col gap-6 h-full">
            {/* Selected User Details - takes 50% of remaining height */}
            <div className="flex-1 overflow-y-auto"> {/* Removed bg/shadow/padding - moved to User.tsx */}
              <User id={selectedUserId} />
            </div>

            {/* Selected Book Details - takes 50% of remaining height */}
            <div className="flex-1 overflow-y-auto"> {/* Removed bg/shadow/padding - moved to Book.tsx */}
              <Book id={selectedBookId} />
            </div>

            {/* Create Reservation Section - fixed height, at the bottom */}
            <div className="flex flex-col items-center flex-shrink-0"> {/* Removed bg/shadow/padding - keeping only layout */}
              <button
                className={`px-8 py-4 rounded-xl text-xl font-bold transition-all duration-300 ease-in-out w-full
                  ${!isCheckoutDisabled
                    ? "bg-green-600 text-white hover:bg-green-700 shadow-lg transform hover:scale-105"
                    : "bg-neutral-600 text-neutral-400 cursor-not-allowed"
                  }`}
                onClick={handleCreateReservation}
                disabled={isCheckoutDisabled}
              >
                {isCreatingReservation
                  ? "Checking out..."
                  : selectedBookData?.status === 'checked_out' && selectedBookId
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
