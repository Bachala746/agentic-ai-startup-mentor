import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./Home.css";

export default function Home() {
  const navigate = useNavigate();
  const location = useLocation();

  
  const [startupIdea, setStartupIdea] = useState("");
  const [selectedAgent, setSelectedAgent] = useState("Strategy Mentor");

  const handleGeneratePlan = (e) => {
    e.preventDefault();

    if (!startupIdea.trim()) return;

    // Store the selected startup idea
    localStorage.setItem(
      "selectedStartupIdea",
      startupIdea.trim()
    );

    // Store the selected mentor
    localStorage.setItem(
      "selectedMentor",
      selectedAgent
    );

    // Go to the Idea Overview page
    navigate("/idea-overview");
  };

  return (
    <div className="workspace-container">

      {/* Sidebar */}
      <aside className="workspace-sidebar">

        <div className="sidebar-header">
          <h2>AI Startup Mentor</h2>

          <button
            className="new-idea-btn"
            onClick={() => {
              setStartupIdea("");
              setSelectedAgent("Strategy Mentor");
              setActiveTab("workspace");
            }}
          >
            + New Idea
          </button>
        </div>

        <nav className="sidebar-nav">

          <button
            className={`nav-item ${
              location.pathname === "/home" ? "active" : ""
            }`}
            onClick={() => navigate("/home")}
          >
            💡 Startup Workspace
          </button>

          <button
            className="nav-item"
            onClick={() => navigate("/dashboard")}
          >
            🏠 Dashboard
          </button>

          <button
            className="nav-item"
            onClick={() => navigate("/saved-plans")}
          >
            💾 Saved Plans
          </button>

          <button
            className="nav-item"
            onClick={() => navigate("/agent-insights")}
          >
            📊 Agent Insights
          </button>

          <button
            className="nav-item"
            onClick={() => navigate("/profile")}
          >
            ⚙️ User Profile
          </button>

        </nav>

        <div className="sidebar-footer">

          <button
            className="nav-item"
            onClick={() => {
              localStorage.removeItem("currentUserEmail");
              navigate("/login");
            }}
          >
            🚪 Logout
          </button>

        </div>

      </aside>

      {/* Main Workspace */}
      <main className="workspace-main">

        {/* Top Bar */}
        <header className="workspace-topbar">

          <div className="topbar-left">
            <h1>Startup Command Center</h1>

            <p>
              Powered by Google Gemini & LangGraph Multi-Agent Intelligence
            </p>
          </div>

          <div className="topbar-right">

            <div className="agent-status">
              <span className="status-dot"></span>
              Agents Ready
            </div>

            <div className="user-profile-badge">
              Founder Mode
            </div>

          </div>

        </header>

        {/* Main Content */}
        <div className="workspace-content">

          <div className="idea-input-card">

            <h2>
              What are we building today?
            </h2>

            <p>
              Enter your startup idea to first understand the concept,
              then analyze it in detail using our multi-agent AI system.
            </p>

            <form
              onSubmit={handleGeneratePlan}
              className="idea-form"
            >

              {/* Startup Idea */}
              <textarea
                value={startupIdea}
                onChange={(e) =>
                  setStartupIdea(e.target.value)
                }
                placeholder="e.g., An AI-powered platform that helps small businesses manage customer feedback and automatically identify common complaints and improvement areas..."
                required
              />

              {/* Mentor Selection */}
              <div className="agent-selector">

                <span
                  style={{
                    alignSelf: "center",
                    fontSize: "0.85rem",
                    color: "#94a3b8",
                  }}
                >
                  Primary Mentor:
                </span>

                {[
                  "Strategy Mentor",
                  "Pitch Deck Coach",
                  "Tech Architect",
                ].map((agent) => (

                  <button
                    type="button"
                    key={agent}
                    className={`agent-chip ${
                      selectedAgent === agent
                        ? "active"
                        : ""
                    }`}
                    onClick={() =>
                      setSelectedAgent(agent)
                    }
                  >
                    {agent}
                  </button>

                ))}

              </div>

              {/* Submit */}
              <button
                type="submit"
                className="submit-agent-btn"
              >
                Continue to Idea Overview →
              </button>

            </form>

          </div>

        </div>

      </main>

    </div>
  );
}