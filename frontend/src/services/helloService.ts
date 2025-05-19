import api from "./api";
import type { HelloResponse } from "../types/hello";

export async function fetchHello(): Promise<HelloResponse> {
  const response = await api.get<HelloResponse>("/hello");
  return response.data;
}
