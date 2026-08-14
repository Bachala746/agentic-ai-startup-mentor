import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

export default function Dashboard() {
  const navigate = useNavigate();

  const [startupIdea, setStartupIdea] = useState("");
  const [selectedMentor, setSelectedMentor] = useState("Strategy Mentor");
  const [isGenerated, setIsGenerated] = useState(false);
  const [loading, setLoading] = useState(false);

  const [chatMessage, setChatMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([
    {
      sender: "AI Mentor",
      text: "Welcome, Founder! Tell me about your startup idea and let's build it together."
    }
  ]);

  const handleGenerate = (e) => {
    e.preventDefault();

    if (!startupIdea.trim()) {
      alert("Please enter your startup idea first!");
      return;
    }

    setLoading(true);

    setTimeout(() => {
      setLoading(false);
      setIsGenerated(true);
    }, 700);
  };

  const handleSendMessage = (e) => {
    e.preventDefault();

    if (!chatMessage.trim()) return;

    setChatHistory((prev) => [
      ...prev,
      { sender: "You", text: chatMessage }
    ]);

    setChatMessage("");

    setTimeout(() => {
      setChatHistory((prev) => [
        ...prev,
        {
          sender: "AI Mentor",
          text: `That's an interesting direction. Your ${selectedMentor.toLowerCase()} can help validate "${startupIdea}".`
        }
      ]);
    }, 500);
  };

  return (
    <div className="dashboard-page">

      {/* Sidebar */}
      <aside className="dashboard-sidebar">

        <div className="sidebar-logo">
          <div className="logo-icon">🚀</div>
          <div>
            <h2>AI Startup Mentor</h2>
            <span>Founder Workspace</span>
          </div>
        </div>

        <nav className="sidebar-nav">

          <button className="nav-item active">
            <span>💡</span>
            Startup Workspace
          </button>

          <button className="nav-item">
            <span>📁</span>
            Saved Plans
          </button>

          <button className="nav-item">
            <span>📊</span>
            Agent Insights
          </button>

          <button
            className="nav-item"
            onClick={() => navigate("/profile")}
          >
            <span>⚙️</span>
            User Profile
          </button>

        </nav>

        <button
          className="logout-button"
          onClick={() => navigate("/login")}
        >
          🚪 Logout
        </button>

      </aside>


      {/* Main Content */}
      <main className="dashboard-main">

        {/* Header */}
        <header className="dashboard-header">

          <div>
            <h1>Startup Command Center</h1>
            <p>Turn your idea into an actionable startup roadmap.</p>
          </div>

          <div className="header-actions">

            <div className="agent-status">
              <span className="status-dot"></span>
              Agent Online
            </div>

            <button
              className="profile-button"
              onClick={() => navigate("/profile")}
            >
              Founder Mode
            </button>

          </div>

        </header>


        {/* Welcome */}
        <section className="welcome-card">

          <div>
            <span className="welcome-label">YOUR AI CO-FOUNDER</span>

            <h2>
              What are we building today?
            </h2>

            <p>
              Describe your startup idea and choose the AI mentor
              that will guide your next steps.
            </p>
          </div>

        </section>


        {/* Idea Builder */}
        <section className="builder-card">

          <div className="section-title">
            <span className="step-number">01</span>

            <div>
              <h3>Describe your startup idea</h3>
              <p>Give your idea in simple words. You can refine it later.</p>
            </div>
          </div>

          <textarea
            className="idea-input"
            value={startupIdea}
            onChange={(e) => setStartupIdea(e.target.value)}
            placeholder="Example: An AI platform that helps college students find personalized career paths..."
          />


          {/* Mentor */}
          <div className="section-title mentor-title">

            <span className="step-number">02</span>

            <div>
              <h3>Choose your AI mentor</h3>
              <p>Select the type of guidance you need.</p>
            </div>

          </div>


          <div className="mentor-grid">

            {[
              {
                name: "Strategy Mentor",
                icon: "🎯",
                description: "Business & market strategy"
              },
              {
                name: "Pitch Deck Coach",
                icon: "📈",
                description: "Pitch & investor preparation"
              },
              {
                name: "Tech Architect",
                icon: "⚙️",
                description: "Technology & architecture"
              }
            ].map((mentor) => (

              <button
                key={mentor.name}
                type="button"
                className={`mentor-card ${
                  selectedMentor === mentor.name ? "selected" : ""
                }`}
                onClick={() => setSelectedMentor(mentor.name)}
              >

                <span className="mentor-icon">
                  {mentor.icon}
                </span>

                <div>
                  <strong>{mentor.name}</strong>
                  <small>{mentor.description}</small>
                </div>

                <span className="selection-circle">
                  {selectedMentor === mentor.name ? "✓" : ""}
                </span>

              </button>

            ))}

          </div>


          {/* Generate */}
          <button
            className="generate-button"
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading
              ? "Analyzing Your Idea..."
              : "Activate AI Mentorship 🚀"}
          </button>

        </section>


        {/* Generated Plan */}
        {isGenerated && (

          <section className="analysis-card">

            <div className="analysis-header">
              <div>
                <span>AI ANALYSIS</span>
                <h2>Your Startup Roadmap</h2>
              </div>

              <div className="mentor-badge">
                {selectedMentor}
              </div>
            </div>

            <div className="idea-preview">
              <span>Your Idea</span>
              <p>{startupIdea}</p>
            </div>

            <div className="analysis-grid">

              <div className="analysis-item">
                <span>01</span>
                <h3>Problem</h3>
                <p>
                  Identify the main problem your startup solves
                  and why customers need a better solution.
                </p>
              </div>

              <div className="analysis-item">
                <span>02</span>
                <h3>Target Customers</h3>
                <p>
                  Define the people most likely to use and pay
                  for your product.
                </p>
              </div>

              <div className="analysis-item">
                <span>03</span>
                <h3>Business Model</h3>
                <p>
                  Explore possible revenue models and
                  monetization strategies.
                </p>
              </div>

              <div className="analysis-item">
                <span>04</span>
                <h3>Next Steps</h3>
                <p>
                  Build, validate, test and improve your MVP
                  step by step.
                </p>
              </div>

            </div>

          </section>

        )}


        {/* AI Chat */}
        <section className="chat-card">

          <div className="chat-header">

            <div>
              <span className="chat-icon">🤖</span>

              <div>
                <h3>AI Mentor Chat</h3>
                <p>{selectedMentor} is ready to help</p>
              </div>
            </div>

            <span className="online-label">
              ● Online
            </span>

          </div>


          <div className="chat-messages">

            {chatHistory.map((message, index) => (

              <div
                key={index}
                className={`chat-message ${
                  message.sender === "You"
                    ? "user-message"
                    : "ai-message"
                }`}
              >

                <strong>{message.sender}</strong>

                <p>{message.text}</p>

              </div>

            ))}

          </div>


          <form
            className="chat-input-area"
            onSubmit={handleSendMessage}
          >

            <input
              type="text"
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              placeholder="Ask your AI mentor anything..."
            />

            <button type="submit">
              Send ➤
            </button>

          </form>

        </section>

      </main>

    </div>
  );
}