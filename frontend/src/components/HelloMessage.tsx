import React, { useEffect, useState } from "react";
import { fetchHello } from "../services/helloService";

const HelloMessage: React.FC = () => {
  const [message, setMessage] = useState<string>("Loading...");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHello()
      .then((data) => setMessage(data.message))
      .catch((err) => {
        console.error(err);
        setError("Something went wrong");
      });
  }, []);

  return (
    <div>
      <h2>Hello from Backend:</h2>
      <p>{error || message}</p>
    </div>
  );
};

export default HelloMessage;
