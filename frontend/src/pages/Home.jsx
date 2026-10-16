import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./Home.css";

export default function Home() {
  const navigate = useNavigate();
  const location = useLocation();

  // State
  const [activeTab, setActiveTab] = useState("workspace");
  const [ideaFlow, setIdeaFlow] = useState("has-idea"); // "has-idea" | "no-idea"
  const [startupIdea, setStartupIdea] = useState("");
  const [selectedAgent, setSelectedAgent] = useState("Strategy Mentor");

  const handleGeneratePlan = (e) => {
    e.preventDefault();

    if (!startupIdea.trim()) return;

    // Store the selected startup idea
    localStorage.setItem("selectedStartupIdea", startupIdea.trim());

    // Store the selected mentor
    localStorage.setItem("selectedMentor", selectedAgent);

    // Go to the Idea Overview page
    navigate("/idea-overview");
  };

  const handleResetWorkspace = () => {
    setStartupIdea("");
    setSelectedAgent("Strategy Mentor");
    setIdeaFlow("has-idea");
    setActiveTab("workspace");
  };

  return (
    <div className="workspace-container">
      {/* Sidebar */}
      <aside className="workspace-sidebar">
        <div className="sidebar-header">
          <h2>AI Startup Mentor</h2>

          <button className="new-idea-btn" onClick={handleResetWorkspace}>
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

            <div className="user-profile-badge">Founder Mode</div>
          </div>
        </header>

        {/* Main Content */}
        <div className="workspace-content">
          <div className="idea-input-card">
            <h2>What are we building today?</h2>

            <p>
              Choose your path below to either analyze an existing concept or
              discover personalized startup opportunities.
            </p>

            {/* Path Selection Cards */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
                gap: "1rem",
                margin: "1.5rem 0",
              }}
            >
              {/* Option 1: Has Idea */}
              <div
                role="button"
                tabIndex={0}
                onClick={() => setIdeaFlow("has-idea")}
                onKeyDown={(e) => e.key === "Enter" && setIdeaFlow("has-idea")}
                style={{
                  padding: "1.25rem",
                  borderRadius: "12px",
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "all 0.2s ease-in-out",
                  border:
                    ideaFlow === "has-idea"
                      ? "2px solid #3b82f6"
                      : "1px solid rgba(255, 255, 255, 0.12)",
                  backgroundColor:
                    ideaFlow === "has-idea"
                      ? "rgba(59, 130, 246, 0.12)"
                      : "rgba(255, 255, 255, 0.03)",
                  boxShadow:
                    ideaFlow === "has-idea"
                      ? "0 4px 14px rgba(59, 130, 246, 0.2)"
                      : "none",
                }}
              >
                <div style={{ fontSize: "1.4rem", marginBottom: "0.4rem" }}>
                  💡
                </div>
                <h3
                  style={{
                    fontSize: "1.05rem",
                    fontWeight: "600",
                    margin: "0 0 0.35rem 0",
                    color: ideaFlow === "has-idea" ? "#60a5fa" : "#f8fafc",
                  }}
                >
                  I Have a Startup Idea
                </h3>
                <p
                  style={{
                    margin: 0,
                    fontSize: "0.85rem",
                    color: "#94a3b8",
                    lineHeight: 1.45,
                  }}
                >
                  I already have an idea and want to analyze it.
                </p>
              </div>

              {/* Option 2: Needs Idea */}
              <div
                role="button"
                tabIndex={0}
                onClick={() => setIdeaFlow("no-idea")}
                onKeyDown={(e) => e.key === "Enter" && setIdeaFlow("no-idea")}
                style={{
                  padding: "1.25rem",
                  borderRadius: "12px",
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "all 0.2s ease-in-out",
                  border:
                    ideaFlow === "no-idea"
                      ? "2px solid #3b82f6"
                      : "1px solid rgba(255, 255, 255, 0.12)",
                  backgroundColor:
                    ideaFlow === "no-idea"
                      ? "rgba(59, 130, 246, 0.12)"
                      : "rgba(255, 255, 255, 0.03)",
                  boxShadow:
                    ideaFlow === "no-idea"
                      ? "0 4px 14px rgba(59, 130, 246, 0.2)"
                      : "none",
                }}
              >
                <div style={{ fontSize: "1.4rem", marginBottom: "0.4rem" }}>
                  🎯
                </div>
                <h3
                  style={{
                    fontSize: "1.05rem",
                    fontWeight: "600",
                    margin: "0 0 0.35rem 0",
                    color: ideaFlow === "no-idea" ? "#60a5fa" : "#f8fafc",
                  }}
                >
                  I Don't Have a Startup Idea
                </h3>
                <p
                  style={{
                    margin: 0,
                    fontSize: "0.85rem",
                    color: "#94a3b8",
                    lineHeight: 1.45,
                  }}
                >
                  Help me discover startup ideas based on my profile.
                </p>
              </div>
            </div>

            {/* FLOW 1: User Has an Idea */}
            {ideaFlow === "has-idea" && (
              <form onSubmit={handleGeneratePlan} className="idea-form">
                {/* Startup Idea */}
                <textarea
                  value={startupIdea}
                  onChange={(e) => setStartupIdea(e.target.value)}
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
                        selectedAgent === agent ? "active" : ""
                      }`}
                      onClick={() => setSelectedAgent(agent)}
                    >
                      {agent}
                    </button>
                  ))}
                </div>

                {/* Submit */}
                <button type="submit" className="submit-agent-btn">
                  Continue to Idea Overview →
                </button>
              </form>
            )}

            {/* FLOW 2: User Doesn't Have an Idea */}
            {ideaFlow === "no-idea" && (
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "1.25rem",
                  padding: "1.75rem",
                  borderRadius: "12px",
                  backgroundColor: "rgba(255, 255, 255, 0.02)",
                  border: "1px dashed rgba(255, 255, 255, 0.15)",
                  marginTop: "0.5rem",
                }}
              >
                <div>
                  <h3
                    style={{
                      margin: "0 0 0.5rem 0",
                      fontSize: "1.1rem",
                      color: "#f8fafc",
                    }}
                  >
                    Generate Ideas from Your Founder Profile
                  </h3>
                  <p
                    style={{
                      margin: 0,
                      fontSize: "0.9rem",
                      color: "#94a3b8",
                      lineHeight: 1.5,
                    }}
                  >
                    We will analyze your personal strengths, domain background,
                    and target markets to generate curated, high-potential
                    startup opportunities tailored to you.
                  </p>
                </div>

                <button
                  type="button"
                  className="submit-agent-btn"
                  onClick={() => navigate("/profile-idea-generation")}
                >
                  Discover Ideas from My Profile →
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}