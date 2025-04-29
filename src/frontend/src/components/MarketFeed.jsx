import React, { useState, useEffect } from "react";

const MarketFeed = () => {
  const [feed, setFeed] = useState(null);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("Received:", data);

      setFeed(data);
    };

    ws.onclose = () => {
      console.log("WebSocket closed. Reconnecting in 3 seconds...");
      setTimeout(() => {
        window.location.reload();
      }, 3000);
    };

    return () => ws.close();
  }, []);

  return (
    <div>
      {feed ? (
        <div>
          <h2>Feed Received</h2>
          <pre style={{ textAlign: "left", backgroundColor: "#f5f5f5", padding: "10px" }}>
            {JSON.stringify(feed, null, 2)}
          </pre>
        </div>
      ) : (
        <h2>Connecting...</h2>
      )}
    </div>
  );
};

export default MarketFeed;
