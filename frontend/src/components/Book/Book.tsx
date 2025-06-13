import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchBookById } from "../../services/bookService";
import { formatDate } from "../../utils/dateUtils";

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
      <div className="p-4 bg-neutral-700 rounded-lg text-neutral-400">
        <h2 className="text-xl font-semibold mb-2 text-neutral-200">Book Details</h2>
        <p>Please select a book to view its details.</p>
      </div>
    );
  }

  if (isLoading) return <p className="text-neutral-400">Loading book...</p>;
  if (error) return <p className="text-red-500">Error loading book: {(error as Error).message}</p>;

  return (
    <div className="book p-4 bg-neutral-700 rounded-lg shadow-inner">
      <h2 className="text-xl font-semibold mb-3 text-neutral-200">Book Details</h2>
      <p className="mb-1"><strong className="text-neutral-300">Title:</strong> {data?.title}</p>
      <p className="mb-1"><strong className="text-neutral-300">Status:</strong> <span className={`${data?.status === 'available' ? 'text-green-400' : 'text-orange-400'}`}>{data?.status}</span></p>
      <p><strong className="text-neutral-300">Created At:</strong> {formatDate(data?.created_at)}</p>
    </div>
  );
};

export default Book;
