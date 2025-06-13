import { useQuery } from "@tanstack/react-query";
import "./BookList.scss";
import { useState } from "react";
import { fetchBooks } from "../../services/bookService";

interface BookListProps {
  onSelectBook: (userId: string) => void;
}

const BookList: React.FC<BookListProps> = ({ onSelectBook }) => {
  const { data, error, isLoading } = useQuery({
    queryKey: ["books"],
    queryFn: () => fetchBooks(),
  });
  const [searchInput, setSearchInput] = useState("");

  if (isLoading) return <p>Loading books...</p>;
  if (error) return <p>Error loading books: {error.message}</p>;

  const books = data?.books;
  const filteredBooks = books?.filter(book =>
    book.title.toLowerCase().includes(searchInput.toLowerCase())
  ) || [];

  return (
    <div className="user-list">
      <h2>Books</h2>
      <input
        type="text"
        placeholder="Search users..."
        value={searchInput}
        onChange={e => setSearchInput(e.target.value)}
        className="user-list__search"
        style={{ marginBottom: "20px" }}
      />
      <ul className="user-list__items">
        {filteredBooks.map(book => (
          <li
            key={book.book_id}
            className="user-list__item"
            onClick={() => onSelectBook(book.book_id)}
          >
            {book.title}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default BookList;
