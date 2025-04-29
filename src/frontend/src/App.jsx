import React from "react";
import MarketFeed from "./components/MarketFeed.jsx";

function App() {
  return (
    <div style={{ padding: "20px", fontFamily: "sans-serif" }}>
      <h1>📈 Live Market Dashboard</h1>
      <MarketFeed />
    </div>
  );
}

export default App;
