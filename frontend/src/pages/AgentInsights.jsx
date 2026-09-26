import { useNavigate } from "react-router-dom";
import "./AgentInsights.css";

export default function AgentInsights() {
  const navigate = useNavigate();

  return (
    <div className="insights-page">

      {/* Sidebar */}
      <aside className="insights-sidebar">

        <div>
          <div className="insights-logo">
            <h2>AI Startup Mentor</h2>
          </div>

          <button
            className="insights-new-idea-btn"
            onClick={() => navigate("/home")}
          >
            + New Idea
          </button>

          <nav className="insights-nav">

            <button onClick={() => navigate("/home")}>
              💡 Startup Workspace
            </button>

            <button onClick={() => navigate("/dashboard")}>
              🏠 Dashboard
            </button>

            <button onClick={() => navigate("/saved-plans")}>
              💾 Saved Plans
            </button>

            <button className="insights-active">
              📊 Agent Insights
            </button>

            <button onClick={() => navigate("/profile")}>
              ⚙️ User Profile
            </button>

          </nav>
        </div>

        <div className="insights-sidebar-footer">
          <button
            onClick={() => {
              localStorage.removeItem("currentUserEmail");
              navigate("/login");
            }}
          >
            📕 Logout
          </button>
        </div>

      </aside>

      {/* Main Content */}
      <main className="insights-main">

        <header className="insights-header">

          <div>
            <h1>Agent Insights</h1>

            <p>
              Understand how the multi-agent system analyzes
              your startup idea.
            </p>
          </div>

          <div className="insights-status">
            <span></span>
            Agents Ready
          </div>

        </header>

        <section className="insights-content">

          <div className="insights-intro">

            <div className="insights-intro-icon">
              🤖
            </div>

            <div>
              <h2>
                How Your Startup Is Analyzed
              </h2>

              <p>
                Your startup idea passes through multiple
                specialized AI agents. Each agent focuses on
                a different part of the startup analysis.
              </p>
            </div>

          </div>

          <div className="agent-flow">

            {/* Market Agent */}
            <div className="agent-card">

              <div className="agent-card-icon">
                📊
              </div>

              <div className="agent-card-content">

                <div className="agent-card-title">
                  <span className="agent-number">
                    01
                  </span>

                  <h2>Market Agent</h2>
                </div>

                <p>
                  Analyzes <strong>target customers</strong>,
                  market demand, competitors, opportunities,
                  and market gaps.
                </p>

                <div className="agent-tags">
                  <span>Customers</span>
                  <span>Demand</span>
                  <span>Competitors</span>
                  <span>Market Gaps</span>
                </div>

              </div>

            </div>

            <div className="agent-connector">
              ↓
            </div>

            {/* Finance Agent */}
            <div className="agent-card">

              <div className="agent-card-icon">
                💰
              </div>

              <div className="agent-card-content">

                <div className="agent-card-title">
                  <span className="agent-number">
                    02
                  </span>

                  <h2>Finance Agent</h2>
                </div>

                <p>
                  Analyzes <strong>financial feasibility</strong>,
                  expenses, revenue models, budget constraints,
                  and low-cost MVP possibilities.
                </p>

                <div className="agent-tags">
                  <span>Budget</span>
                  <span>Expenses</span>
                  <span>Revenue</span>
                  <span>MVP</span>
                </div>

              </div>

            </div>

            <div className="agent-connector">
              ↓
            </div>

            {/* Risk Agent */}
            <div className="agent-card">

              <div className="agent-card-icon">
                ⚠️
              </div>

              <div className="agent-card-content">

                <div className="agent-card-title">
                  <span className="agent-number">
                    03
                  </span>

                  <h2>Risk Agent</h2>
                </div>

                <p>
                  Identifies <strong>market, financial,
                  technical, customer adoption,</strong> and
                  implementation risks.
                </p>

                <div className="agent-tags">
                  <span>Market Risk</span>
                  <span>Financial Risk</span>
                  <span>Technical Risk</span>
                  <span>Adoption Risk</span>
                </div>

              </div>

            </div>

            <div className="agent-connector">
              ↓
            </div>

            {/* Decision Agent */}
            <div className="agent-card decision-agent">

              <div className="agent-card-icon">
                🎯
              </div>

              <div className="agent-card-content">

                <div className="agent-card-title">
                  <span className="agent-number">
                    04
                  </span>

                  <h2>Decision Agent</h2>
                </div>

                <p>
                  Combines the outputs from all agents and
                  creates the <strong>final recommendation
                  and startup roadmap.</strong>
                </p>

                <div className="agent-tags">
                  <span>Final Analysis</span>
                  <span>Recommendation</span>
                  <span>Roadmap</span>
                </div>

              </div>

            </div>

          </div>

          <div className="insights-footer-note">
            💡 The agents work together through the
            <strong> LangGraph workflow</strong> to produce
            a personalized startup analysis.
          </div>

        </section>

      </main>

    </div>
  );
}