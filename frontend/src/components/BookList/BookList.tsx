import { useQuery } from "@tanstack/react-query";
import { fetchBooks } from "../../services/bookService";
import SelectableList from "../SelectableList/SelectableList";
import type { Book } from "../../types/book";

interface BookListProps {
  selectedBookId: string | null;
  onSelectBook: (bookId: string) => void;
}

const BookList: React.FC<BookListProps> = ({ selectedBookId, onSelectBook }) => {
  const { data, error, isLoading } = useQuery({
    queryKey: ["books"],
    queryFn: () => fetchBooks(),
  });

  const books = data?.books ?? [];

  return (
    <div>
      <SelectableList<Book>
        data={books}
        isLoading={isLoading}
        error={error}
        extractId={(book) => book.book_id}
        extractLabel={(book) => book.title}
        onSelect={onSelectBook}
        searchPlaceholder="Search books..."
        selectedId={selectedBookId}
      />
    </div>
  );
};

export default BookList;
