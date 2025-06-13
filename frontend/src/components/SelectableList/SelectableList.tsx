import { useState } from "react";
import "./SelectableList.scss";

interface SelectableListProps<T> {
  data: T[];
  isLoading: boolean;
  error: unknown;
  extractId: (item: T) => string;
  extractLabel: (item: T) => string;
  onSelect: (id: string) => void;
  searchPlaceholder?: string;
}

function SelectableList<T>({
  data,
  isLoading,
  error,
  extractId,
  extractLabel,
  onSelect,
  searchPlaceholder = "Search..."
}: SelectableListProps<T>) {
  const [searchInput, setSearchInput] = useState("");

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error: {(error as Error).message}</p>;

  const filteredItems = data.filter(item =>
    extractLabel(item).toLowerCase().includes(searchInput.toLowerCase())
  );

  return (
    <div className="selectable-list">
      <input
        type="text"
        placeholder={searchPlaceholder}
        value={searchInput}
        onChange={(e) => setSearchInput(e.target.value)}
        className="selectable-list__search"
        style={{ marginBottom: "20px" }}
      />
      <ul className="selectable-list__items">
        {filteredItems.map((item) => (
          <li
            key={extractId(item)}
            className="selectable-list__item"
            onClick={() => onSelect(extractId(item))}
          >
            {extractLabel(item)}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default SelectableList;
