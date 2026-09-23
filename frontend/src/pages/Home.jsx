import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Home.css";

export default function Home() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("workspace");
  const [startupIdea, setStartupIdea] = useState("");
  const [selectedAgent, setSelectedAgent] = useState("Strategy Mentor");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedPlan, setGeneratedPlan] = useState(null);
  const [chatMessages, setChatMessages] = useState([
    { sender: "ai", text: "Hello! I am your Agentic AI Startup Mentor. Feed me your idea, and let's build a solid execution plan." }
  ]);
  const [chatInput, setChatInput] = useState("");

  const handleGeneratePlan = (e) => {
    e.preventDefault();
    if (!startupIdea.trim()) return;

    setIsGenerating(true);

    // Simulate AI Agent processing via n8n / Gemini
    setTimeout(() => {
      setGeneratedPlan({
        title: startupIdea.slice(0, 40) + "...",
        overview: "A disruptive platform leveraging modern tech to solve inefficiencies in the target market.",
        targetAudience: ["Tech-savvy professionals", "SME business owners", "Early adopters"],
        monetization: "SaaS Tiered Subscription Model ($29/mo to $199/mo)",
        actionSteps: [
          "Validate core hypothesis via landing page smoke test.",
          "Build Minimum Viable Product (MVP) using React and Node.",
          "Launch on Product Hunt and relevant developer communities."
        ]
      });
      setIsGenerating(false);
      setActiveTab("workspace");
    }, 2000);
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const newMsg = { sender: "user", text: chatInput };
    setChatMessages((prev) => [...prev, newMsg]);
    setChatInput("");

    // Simulate AI response
    setTimeout(() => {
      setChatMessages((prev) => [
        ...prev,
        { sender: "ai", text: `That's a strong point regarding your ${selectedAgent.toLowerCase()} focus. Let's ensure your feedback loops validate this assumption early.` }
      ]);
    }, 1000);
  };

  return (
    <div className="workspace-container">
      {/* Sidebar */}
      <aside className="workspace-sidebar">
        <div className="sidebar-header">
          <h2>AI Startup Mentor</h2>
          <button className="new-idea-btn" onClick={() => { setGeneratedPlan(null); setStartupIdea(""); }}>
            + New Idea
          </button>
        </div>

        <nav className="sidebar-nav">
          <button 
            className={`nav-item ${activeTab === "workspace" ? "active" : ""}`}
            onClick={() => setActiveTab("workspace")}
          >
            💡 Startup Workspace
          </button>
          <button
            className="nav-item"
            onClick={() => navigate("/dashboard")}
          >
            🏠 Dashboard
          </button>
          <button className="nav-item" onClick={() => navigate("/saved-plans")}>
            💾 Saved Plans
          </button>

          <button 
            className={`nav-item ${activeTab === "analytics" ? "active" : ""}`}
            onClick={() => navigate("/agent-insights")}
          >
            📊 Agent Insights
          </button>
          <button 
            className={`nav-item ${activeTab === "profile" ? "active" : ""}`}
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
        <header className="workspace-topbar">
          <div className="topbar-left">
            <h1>Startup Command Center</h1>
            <p>Powered by Google Gemini & LangGraph Multi-Agent Intelligence</p>
          </div>
          <div className="topbar-right">
            <div className="agent-status">
              <span className="status-dot"></span>
              Agents Online ({selectedAgent})
            </div>
            <div className="user-profile-badge">Founder Mode</div>
          </div>
        </header>

        <div className="workspace-content">
          {!generatedPlan ? (
            <div className="idea-input-card">
              <h2>What are we building today?</h2>
              <p>Describe your startup concept in detail. Our multi-agent AI framework will analyze market viability, revenue models, and step-by-step execution.</p>
              
              <form onSubmit={handleGeneratePlan} className="idea-form">
                <textarea
                  value={startupIdea}
                  onChange={(e) => setStartupIdea(e.target.value)}
                  placeholder="e.g., An AI-powered fitness app that creates hyper-personalized workout routines based on real-time biometric data and daily nutrition logs..."
                  required
                />

                <div className="agent-selector">
                  <span style={{ alignSelf: "center", fontSize: "0.85rem", color: "#94a3b8" }}>Primary Mentor:</span>
                  {["Strategy Mentor", "Pitch Deck Coach", "Tech Architect"].map((agent) => (
                    <button
                      type="button"
                      key={agent}
                      className={`agent-chip ${selectedAgent === agent ? "active" : ""}`}
                      onClick={() => setSelectedAgent(agent)}
                    >
                      {agent}
                    </button>
                  ))}
                </div>

                <button type="submit" className="submit-agent-btn" disabled={isGenerating}>
                  {isGenerating ? "Agents are analyzing your idea..." : "Activate AI Mentorship 🚀"}
                </button>
              </form>
            </div>
          ) : (
            <div className="plan-dashboard">
              <div className="plan-grid">
                <div className="plan-card">
                  <h3>🎯 Executive Overview</h3>
                  <p>{generatedPlan.overview}</p>
                </div>

                <div className="plan-card">
                  <h3>👥 Target Audience</h3>
                  <ul>
                    {generatedPlan.targetAudience.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>

                <div className="plan-card">
                  <h3>💰 Monetization Strategy</h3>
                  <p>{generatedPlan.monetization}</p>
                </div>
              </div>

              <div className="plan-card">
                <h3>⚡ Step-by-Step Action Plan</h3>
                <ul>
                  {generatedPlan.actionSteps.map((step, idx) => (
                    <li key={idx} style={{ marginBottom: "8px" }}>{step}</li>
                  ))}
                </ul>
              </div>

              {/* Interactive AI Chat Section */}
              <div className="chat-section">
                <h3>💬 Ask your {selectedAgent}</h3>
                <div className="chat-box">
                  {chatMessages.map((msg, index) => (
                    <div key={index} className={`chat-message ${msg.sender}`}>
                      {msg.text}
                    </div>
                  ))}
                </div>
                <form onSubmit={handleSendMessage} className="chat-input-form">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Ask follow-up questions about marketing, tech stack, or funding..."
                  />
                  <button type="submit">Send</button>
                </form>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}