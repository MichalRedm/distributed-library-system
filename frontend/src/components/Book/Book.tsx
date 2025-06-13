import { useEffect } from "react";

interface BookProps {
  id: string | null;
}

const Book: React.FC<BookProps> = ({ id }) => {
  useEffect(() => {
    console.log("Loading book with ID:", id);
  }, [id]);

  return (
    <div className="book">
      <h2>Book Details</h2>
      {id === null ? (
        <p>Please select a book to view its details.</p>
      ) : (
        <p>Book ID: {id}</p>
      )}
    </div>
  );
};

export default Book;
