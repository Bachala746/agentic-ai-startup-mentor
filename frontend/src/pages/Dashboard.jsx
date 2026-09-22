import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

export default function Dashboard() {
  const navigate = useNavigate();

  const [founderProfile, setFounderProfile] = useState(null);
  const [startupIdea, setStartupIdea] = useState("");
  const [selectedMentor, setSelectedMentor] = useState("Strategy Mentor");
  const [generatedPlan, setGeneratedPlan] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const [chatMessage, setChatMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([
    {
      sender: "AI",
      text: "Hi Founder! I'm ready to help you build your startup."
    }
  ]);

  useEffect(() => {
    const currentUserEmail = localStorage.getItem("currentUserEmail");

    if (!currentUserEmail) return;

    const users = JSON.parse(
      localStorage.getItem("startupUsers") || "{}"
    );

    const user = users[currentUserEmail];

    if (user?.profile) {
      setFounderProfile(user.profile);
    }
  }, []);

  const mentors = [
    {
      name: "Strategy Mentor",
      icon: "🎯",
      description: "Business strategy & market planning"
    },
    {
      name: "Pitch Deck Coach",
      icon: "📊",
      description: "Pitch preparation & investor guidance"
    },
    {
      name: "Tech Architect",
      icon: "⚙️",
      description: "Technology & product architecture"
    }
  ];

  const handleGenerate = async (e) => {
    e.preventDefault();

    if (!startupIdea.trim()) {
      alert("Please enter your startup idea first!");
      return;
    }

    setIsGenerating(true);
    setGeneratedPlan(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/startup-plan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          startupIdea: startupIdea,
          founderProfile: founderProfile,
          mentor: selectedMentor,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to generate startup plan");
      }

      setGeneratedPlan(data);
    } catch (error) {
      console.error(error);
      alert("Unable to generate the startup plan.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSendMessage = (e) => {
    e.preventDefault();

    if (!chatMessage.trim()) return;

    setChatHistory((prev) => [
      ...prev,
      {
        sender: "You",
        text: chatMessage
      },
      {
        sender: "AI",
        text: `I'll help you with that as your ${selectedMentor}.`
      }
    ]);

    setChatMessage("");
  };

  return (
    <div className="dashboard-page">
      <div className="dashboard-container">

        {/* Header */}
        <header className="dashboard-header">
          <div>
            <h2>🚀 AI Startup Mentor</h2>
            <span>Founder Workspace</span>
          </div>

          <div className="dashboard-nav">
            <button onClick={() => navigate("/home")}>
              Home
            </button>

            <button onClick={() => navigate("/profile")}>
              Profile
            </button>

            <button
              className="logout-btn"
              onClick={() => {
                localStorage.removeItem("currentUserEmail");
                navigate("/login");
              }}
            >
              Logout
            </button>
          </div>
        </header>

        {/* Welcome */}
        <section className="welcome-card">
          <div>
            <span className="welcome-label">
              YOUR AI CO-FOUNDER
            </span>

            <h1>
              Welcome back,{" "}
              {founderProfile?.fullName || "Startup Builder"} 👋
            </h1>

            <p>
              Turn your idea into a personalized startup plan.
            </p>
          </div>

          <div className="status">
            <span></span>
            AI Mentor Online
          </div>
        </section>

        {/* Founder information summary */}
        {founderProfile && (
          <section className="founder-summary">
            <div>
              <span>SKILLS</span>
              <strong>
                {founderProfile.skills || "Not provided"}
              </strong>
            </div>

            <div>
              <span>INTERESTS</span>
              <strong>
                {founderProfile.interests || "Not provided"}
              </strong>
            </div>

            <div>
              <span>BUDGET</span>
              <strong>
                {founderProfile.budget || "Not provided"}
              </strong>
            </div>

            <div>
              <span>GOALS</span>
              <strong>
                {founderProfile.goals || "Not provided"}
              </strong>
            </div>
          </section>
        )}

        {/* Main workspace */}
        <div className="workspace-grid">

          {/* Startup Idea */}
          <section className="dashboard-card idea-card">

            <div className="card-heading">
              <div className="card-icon">💡</div>

              <div>
                <h2>Startup Idea</h2>
                <p>What are you building?</p>
              </div>
            </div>

            <form onSubmit={handleGenerate}>
              <textarea
                value={startupIdea}
                onChange={(e) =>
                  setStartupIdea(e.target.value)
                }
                placeholder="Describe your startup idea in simple words..."
              />

              <button
                className="generate-btn"
                type="submit"
                disabled={isGenerating}
              >
                {isGenerating
                  ? "🤖 Agents Analyzing..."
                  : "🚀 Generate Startup Plan"}
              </button>
            </form>

          </section>

          {/* Mentor Selection */}
          <section className="dashboard-card mentor-card">

            <div className="card-heading">
              <div className="card-icon">🤖</div>

              <div>
                <h2>Choose Your Mentor</h2>
                <p>Select the guidance you need</p>
              </div>
            </div>

            <div className="mentor-grid">
              {mentors.map((mentor) => (
                <button
                  key={mentor.name}
                  type="button"
                  className={`mentor-option ${
                    selectedMentor === mentor.name
                      ? "selected"
                      : ""
                  }`}
                  onClick={() =>
                    setSelectedMentor(mentor.name)
                  }
                >
                  <span className="mentor-icon">
                    {mentor.icon}
                  </span>

                  <strong>{mentor.name}</strong>

                  <small>{mentor.description}</small>
                </button>
              ))}
            </div>

          </section>

        </div>
          {generatedPlan && (
            <section className="dashboard-card results-card">

              <div className="card-heading">
                <div className="card-icon">🧠</div>

                <div>
                  <h2>AI Startup Analysis</h2>
                  <p>Generated by your multi-agent system</p>
                </div>
              </div>

              <div className="result-section">
                <h3>📊 Market Analysis</h3>
                <pre>
                  {JSON.stringify(generatedPlan.market_analysis, null, 2)}
                </pre>
              </div>

              <div className="result-section">
                <h3>💰 Financial Analysis</h3>
                <pre>
                  {JSON.stringify(generatedPlan.financial_analysis, null, 2)}
                </pre>
              </div>

              <div className="result-section">
                <h3>⚠️ Risk Analysis</h3>
                <pre>
                  {JSON.stringify(generatedPlan.risk_analysis, null, 2)}
                </pre>
              </div>

              <div className="result-section">
                <h3>🛣️ Startup Roadmap</h3>
                <ol>
                  {generatedPlan.roadmap?.map((step, index) => (
                    <li key={index}>{step}</li>
                  ))}
                </ol>
              </div>

                            <div className="result-section">
                <h3>🎯 Final Decision</h3>
                <p>{generatedPlan.message}</p>
              </div>

            </section>
          )}

        {/* Active Mentor */}
        <section className="selected-mentor">
          <span>ACTIVE MENTOR</span>
          <strong>{selectedMentor}</strong>
          <p>
            Your selected AI mentor will use your founder
            profile when providing guidance.
          </p>
        </section>

        {/* Chat */}
        <section className="dashboard-card chat-card">

          <div className="card-heading">
            <div className="card-icon">💬</div>

            <div>
              <h2>AI Mentor Chat</h2>
              <p>Ask questions about your startup</p>
            </div>
          </div>

          <div className="chat-history">
            {chatHistory.map((message, index) => (
              <div
                key={index}
                className={`chat-message ${
                  message.sender === "You"
                    ? "user-message"
                    : ""
                }`}
              >
                <strong>{message.sender}</strong>
                <p>{message.text}</p>
              </div>
            ))}
          </div>

          <form
            className="chat-form"
            onSubmit={handleSendMessage}
          >
            <input
              type="text"
              placeholder="Ask your AI mentor..."
              value={chatMessage}
              onChange={(e) =>
                setChatMessage(e.target.value)
              }
            />

            <button type="submit">
              Send
            </button>
          </form>

        </section>

      </div>
    </div>
  );
}