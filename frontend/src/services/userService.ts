import type { User } from "../types/user";

export async function fetchUsers(): Promise<User[]> {
  const response = await fetch("./users.json");
  if (!response.ok) {
    throw new Error("Failed to fetch users");
  }
  return response.json();
}
