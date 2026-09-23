export default function AgentInsights() {
  return (
    <div style={{ padding: "30px", color: "white" }}>
      <h1>📊 Agent Insights</h1>

      <div style={{ marginTop: "25px" }}>
        <h2>📊 Market Agent</h2>
        <p>
          Analyzes target customers, market demand, competitors,
          opportunities, and market gaps.
        </p>
      </div>

      <div style={{ marginTop: "25px" }}>
        <h2>💰 Finance Agent</h2>
        <p>
          Analyzes financial feasibility, expenses, revenue models,
          and low-cost MVP possibilities.
        </p>
      </div>

      <div style={{ marginTop: "25px" }}>
        <h2>⚠️ Risk Agent</h2>
        <p>
          Identifies market, financial, technical, customer adoption,
          and implementation risks.
        </p>
      </div>

      <div style={{ marginTop: "25px" }}>
        <h2>🎯 Decision Agent</h2>
        <p>
          Combines the outputs from all agents and creates the
          final recommendation and startup roadmap.
        </p>
      </div>
    </div>
  );
}