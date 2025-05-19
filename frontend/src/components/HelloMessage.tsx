import React from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchHello } from "../services/helloService";

const HelloMessage: React.FC = () => {
  const { data, error, isLoading } = useQuery({
    queryKey: ["hello"],
    queryFn: fetchHello,
  });

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Something went wrong</p>;

  return (
    <div>
      <h2>Hello from Backend:</h2>
      <p>{data?.message}</p>
    </div>
  );
};

export default HelloMessage;
