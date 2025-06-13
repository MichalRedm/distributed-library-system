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
    return <div className="book"><h2>Book Details</h2><p>Please select a book to view its details.</p></div>;
  }

  if (isLoading) return <p>Loading book...</p>;
  if (error) return <p>Error loading book: {(error as Error).message}</p>;

  return (
    <div className="book">
      <h2>Book Details</h2>
      <p><strong>Title:</strong> {data?.title}</p>
      <p><strong>Status:</strong> {data?.status}</p>
      <p><strong>Created At:</strong> {formatDate(data?.created_at)}</p>
    </div>
  );
};

export default Book;
