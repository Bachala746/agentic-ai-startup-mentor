export default function AgentInsights() {
  return (
    <div
      style={{
        padding: "30px",
        color: "white",
        maxWidth: "1100px",
        margin: "0 auto",
      }}
    >
      <h1>📊 Agent Insights</h1>

      <p style={{ color: "#aeb8ff", marginTop: "8px" }}>
        Understand how the multi-agent system analyzes your startup idea.
      </p>

      {/* Market Agent */}
      <div
        style={{
          marginTop: "25px",
          padding: "22px",
          border: "1px solid #263352",
          borderRadius: "14px",
          background: "#0c1426",
        }}
      >
        <h2>📊 Market Agent</h2>
        <p>
          Analyzes <strong>target customers</strong>, market demand,
          competitors, opportunities, and market gaps.
        </p>
      </div>

      {/* Finance Agent */}
      <div
        style={{
          marginTop: "20px",
          padding: "22px",
          border: "1px solid #263352",
          borderRadius: "14px",
          background: "#0c1426",
        }}
      >
        <h2>💰 Finance Agent</h2>
        <p>
          Analyzes <strong>financial feasibility</strong>, expenses,
          revenue models, budget constraints, and low-cost MVP
          possibilities.
        </p>
      </div>

      {/* Risk Agent */}
      <div
        style={{
          marginTop: "20px",
          padding: "22px",
          border: "1px solid #263352",
          borderRadius: "14px",
          background: "#0c1426",
        }}
      >
        <h2>⚠️ Risk Agent</h2>
        <p>
          Identifies <strong>market, financial, technical, customer
          adoption,</strong> and implementation risks.
        </p>
      </div>

      {/* Decision Agent */}
      <div
        style={{
          marginTop: "20px",
          padding: "22px",
          border: "1px solid #263352",
          borderRadius: "14px",
          background: "#0c1426",
        }}
      >
        <h2>🎯 Decision Agent</h2>
        <p>
          Combines the outputs from all agents and creates the
          <strong> final recommendation</strong> and startup roadmap.
        </p>
      </div>
    </div>
  );
}