import { useState } from "react";

interface SelectableListProps<T> {
  data: T[];
  isLoading: boolean;
  error: unknown;
  extractId: (item: T) => string;
  extractLabel: (item: T) => string;
  onSelect: (id: string) => void;
  searchPlaceholder?: string;
  selectedId?: string | null; // Added to highlight selected item
}

function SelectableList<T>({
  data,
  isLoading,
  error,
  extractId,
  extractLabel,
  onSelect,
  searchPlaceholder = "Search...",
  selectedId // Destructure the new prop
}: SelectableListProps<T>) {
  const [searchInput, setSearchInput] = useState("");

  if (isLoading) return <p className="text-neutral-400">Loading...</p>;
  if (error) return <p className="text-red-500">Error: {(error as Error).message}</p>;

  const filteredItems = data.filter(item =>
    extractLabel(item).toLowerCase().includes(searchInput.toLowerCase())
  );

  return (
    <div className="selectable-list p-2"> {/* Added padding to the container */}
      <input
        type="text"
        placeholder={searchPlaceholder}
        value={searchInput}
        onChange={(e) => setSearchInput(e.target.value)}
        // Tailwind classes for input styling, matching the dark theme
        className="block w-full p-3 rounded-full bg-neutral-600 text-neutral-200 border border-neutral-500 placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4 transition-colors duration-200"
      />
      <ul className="space-y-2 max-h-96 overflow-y-auto pr-2"> {/* Added max-height and overflow for scrollability */}
        {filteredItems.length === 0 && searchInput !== "" && (
          <p className="text-neutral-400 text-center py-4">No matching items found.</p>
        )}
        {filteredItems.map((item) => (
          <li
            key={extractId(item)}
            onClick={() => onSelect(extractId(item))}
            // Tailwind classes for list items, with selection highlighting
            className={`p-3 rounded-lg cursor-pointer transition-colors duration-200
              ${extractId(item) === selectedId
                ? "bg-blue-700 text-white" // Selected style
                : "bg-neutral-700 text-neutral-300 hover:bg-neutral-600" // Default style
              }`}
          >
            {extractLabel(item)}
          </li>
        ))}
      </ul>
      {filteredItems.length === 0 && searchInput === "" && (
        <p className="text-neutral-400 text-center py-4">No items to display.</p>
      )}
    </div>
  );
}

export default SelectableList;
