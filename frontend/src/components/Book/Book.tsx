import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchBookById } from "../../services/bookService";
import { formatDate } from "../../utils/dateUtils";

// Import Font Awesome React components and icons
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBook, faBookOpen } from '@fortawesome/free-solid-svg-icons';

interface BookProps {
  id: string | null;
}

const Book: React.FC<BookProps> = ({ id }) => {
  useEffect(() => {
    if (id) {
      console.log("Loading book with ID:", id);
    }
  }, [id]);

  const { data, error, isLoading } = useQuery({
    queryKey: ["book", id],
    queryFn: () => {
      if (!id) return Promise.reject("No book ID provided");
      return fetchBookById(id);
    },
    enabled: !!id
  });

  if (!id) {
    return (
      <div className="p-4 bg-neutral-700 rounded-lg text-neutral-400 text-center">
        <FontAwesomeIcon icon={faBook} className="text-5xl mb-3 text-neutral-500" /> {/* Book Icon */}
        <p className="text-xl font-semibold mb-2 text-neutral-200">Select a book</p>
        <p>Please select a book to view its details.</p>
      </div>
    );
  }

  if (isLoading) return <p className="text-neutral-400 text-center py-4">Loading book...</p>;
  if (error) return <p className="text-red-500 text-center py-4">Error loading book: {(error as Error).message}</p>;

  return (
    <div className="book p-4 bg-neutral-700 rounded-lg shadow-inner">
      <div className="flex items-center mb-4">
        <FontAwesomeIcon icon={faBookOpen} className="text-5xl mr-4 text-neutral-400" /> {/* Book Icon */}
        <h2 className="text-3xl font-bold text-neutral-100">{data?.title}</h2> {/* Book title as heading */}
      </div>

      <p className="mb-1"><strong className="text-neutral-300">Status:</strong> <span className={`${data?.status === 'available' ? 'text-green-400' : 'text-orange-400'}`}>{data?.status}</span></p>
      <p><strong className="text-neutral-300">Created At:</strong> {formatDate(data?.created_at)}</p>
    </div>
  );
};

export default Book;
