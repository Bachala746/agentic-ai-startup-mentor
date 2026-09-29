import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import "./Dashboard.css";

export default function Dashboard() {
  const navigate = useNavigate();

  const [founderProfile, setFounderProfile] = useState(null);
  const [startupIdea, setStartupIdea] = useState("");
  const [selectedMentor, setSelectedMentor] = useState("Strategy Mentor");
  const [generatedPlan, setGeneratedPlan] = useState(null);
  const [completedSteps, setCompletedSteps] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const [chatMessage, setChatMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([
    {
      sender: "AI",
      text: "Hi Founder! I'm ready to help you build your startup."
    }
  ]);

  useEffect(() => {
    // Get current user
    const currentUserEmail = localStorage.getItem("currentUserEmail");

    if (currentUserEmail) {
      const users = JSON.parse(
        localStorage.getItem("startupUsers") || "{}"
      );

      const user = users[currentUserEmail];

      if (user?.profile) {
        setFounderProfile(user.profile);
      }
    }

    // Get startup idea selected from Home
    const savedStartupIdea =
      localStorage.getItem("selectedStartupIdea");

    if (savedStartupIdea) {
      setStartupIdea(savedStartupIdea);
    }

    // Get mentor selected from Home
    const savedMentor =
      localStorage.getItem("selectedMentor");

    if (savedMentor) {
      setSelectedMentor(savedMentor);
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

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!chatMessage.trim()) return;

    const userMessage = chatMessage;

    setChatHistory((prev) => [
      ...prev,
      {
        sender: "You",
        text: userMessage,
      },
    ]);

    setChatMessage("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/mentor-chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: userMessage,
            startupIdea: startupIdea,
            mentor: selectedMentor,
            founderProfile: founderProfile,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error("Chat request failed");
      }

      setChatHistory((prev) => [
        ...prev,
        {
          sender: "AI",
          text: data.reply,
        },
      ]);
    } catch (error) {
      console.error(error);

      setChatHistory((prev) => [
        ...prev,
        {
          sender: "AI",
          text: "Sorry, I could not connect to the AI mentor right now.",
        },
      ]);
    }
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

                <div className="analysis-item">
                  <h4>Target Customers</h4>
                  <ul>
                    {generatedPlan.market_analysis?.target_customers?.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </div>

                <div className="analysis-item">
                  <h4>Customer Problem</h4>
                  <p>{generatedPlan.market_analysis?.customer_problem}</p>
                </div>

                <div className="analysis-item">
                  <h4>Market Demand</h4>
                  <p>{generatedPlan.market_analysis?.market_demand}</p>
                </div>

                <div className="analysis-item">
                  <h4>Opportunities</h4>
                  <ul>
                    {generatedPlan.market_analysis?.opportunities?.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </div>

                <div className="analysis-item">
                  <h4>Competitors / Alternatives</h4>
                  <ul>
                    {generatedPlan.market_analysis?.competitors_or_alternatives?.map(
                      (item, index) => (
                        <li key={index}>{item}</li>
                      )
                    )}
                  </ul>
                </div>

                <div className="analysis-item">
                  <h4>Market Gaps</h4>
                  <ul>
                    {generatedPlan.market_analysis?.market_gaps?.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </div>

                <div className="analysis-item">
                  <h4>Key Insights</h4>
                  <ul>
                    {generatedPlan.market_analysis?.market_insights?.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="analysis-item">
                <h4>🌐 Current Web Research — Market Trends</h4>

                {generatedPlan.web_sources
                  ?.filter((source) => source.category === "Market Trends")
                  .map((source, index) => (
                    <div key={index} style={{ marginBottom: "20px" }}>
                      <strong>{source.title}</strong>

                      <p>
                        <strong>Source:</strong>{" "}
                        {source.url
                          ? new URL(source.url).hostname
                          : "Web Source"}
                      </p>

                      {source.snippet && <p>{source.snippet}</p>}

                      {source.url && (
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          🔗 View Source
                        </a>
                      )}
                    </div>
                  ))}
              </div>

              <div className="result-section">
                <h3>💰 Financial Analysis</h3>

                <div className="analysis-item">
                  <h4>Financial Practicality</h4>
                  <p>{generatedPlan.financial_analysis?.financial_practicality}</p>
                </div>

                <div className="analysis-item">
                  <h4>Expense Categories</h4>
                  <ul>
                    {generatedPlan.financial_analysis?.expense_categories?.map(
                      (item, index) => (
                        <li key={index}>{item}</li>
                      )
                    )}
                  </ul>
                </div>

                <div className="analysis-item">
                  <h4>Low-Cost MVP Approach</h4>
                  <ul>
                    {generatedPlan.financial_analysis?.low_cost_mvp?.map(
                      (item, index) => (
                        <li key={index}>{item}</li>
                      )
                    )}
                  </ul>
                </div>

                <div className="analysis-item">
                  <h4>Revenue Models</h4>
                  <ul>
                    {generatedPlan.financial_analysis?.revenue_models?.map(
                      (item, index) => (
                        <li key={index}>{item}</li>
                      )
                    )}
                  </ul>
                </div>

                <div className="analysis-item">
                  <h4>Financial Constraints</h4>
                  <ul>
                    {generatedPlan.financial_analysis?.financial_constraints?.map(
                      (item, index) => (
                        <li key={index}>{item}</li>
                      )
                    )}
                  </ul>
                </div>

                <div className="analysis-item">
                  <h4>Recommendations</h4>
                  <ul>
                    {generatedPlan.financial_analysis?.recommendations?.map(
                      (item, index) => (
                        <li key={index}>{item}</li>
                      )
                    )}
                  </ul>
                </div>
              </div>

              <div className="result-section">
                <h3>⚠️ Risk Analysis</h3>

                <div className="analysis-item">
                  <h4>Market Risks</h4>
                  <ul>
                    {generatedPlan.risk_analysis?.market_risks?.map(
                      (item, index) => (
                        <li key={index}>{item}</li>
                      )
                    )}
                  </ul>
                </div>

                <div className="analysis-item">
                  <h4>Financial Risks</h4>
                  <ul>
                    {generatedPlan.risk_analysis?.financial_risks?.map(
                      (item, index) => (
                        <li key={index}>{item}</li>
                      )
                    )}
                  </ul>
                </div>

                <div className="analysis-item">
                  <h4>Product & Technical Risks</h4>
                  <ul>
                    {generatedPlan.risk_analysis?.product_technical_risks?.map(
                      (item, index) => (
                        <li key={index}>{item}</li>
                      )
                    )}
                  </ul>
                </div>

                <div className="analysis-item">
                  <h4>Customer Adoption Risks</h4>
                  <ul>
                    {generatedPlan.risk_analysis?.customer_adoption_risks?.map(
                      (item, index) => (
                        <li key={index}>{item}</li>
                      )
                    )}
                  </ul>
                </div>

                <div className="analysis-item">
                  <h4>Implementation Challenges</h4>
                  <ul>
                    {generatedPlan.risk_analysis?.implementation_challenges?.map(
                      (item, index) => (
                        <li key={index}>{item}</li>
                      )
                    )}
                  </ul>
                </div>

                <div className="analysis-item">
                  <h4>Mitigation Strategies</h4>
                  <ul>
                    {generatedPlan.risk_analysis?.mitigation_strategies?.map(
                      (item, index) => (
                        <li key={index}>{item}</li>
                      )
                    )}
                  </ul>
                </div>
              </div>

              <div className="result-section">
                <h3>🛣️ Startup Roadmap</h3>
                <ol>
                  {generatedPlan.roadmap?.map((step, index) => (
                    <li key={index} style={{ marginBottom: "10px" }}>
                      <label style={{ cursor: "pointer" }}>
                        <input
                          type="checkbox"
                          checked={completedSteps.includes(index)}
                          onChange={() => {
                            setCompletedSteps((prev) =>
                              prev.includes(index)
                                ? prev.filter((item) => item !== index)
                                : [...prev, index]
                            );
                          }}
                        />

                        <span style={{ marginLeft: "10px" }}>
                          {step}
                        </span>
                      </label>
                    </li>
                  ))}
                </ol>
              </div>

              <div className="result-section">
                <h3>🎯 Final Decision</h3>
                <p>{generatedPlan.message}</p>
              </div>
              <div className="save-plan-container">
                <button
                  className="save-plan-btn"
                  onClick={async () => {
                    try {
                      const currentUserEmail =
                        localStorage.getItem("currentUserEmail") || "";

                      const response = await fetch("http://127.0.0.1:8000/save-plan", {
                        method: "POST",
                        headers: {
                          "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                          userEmail: currentUserEmail,
                          startupIdea: startupIdea,
                          mentor: selectedMentor,
                          marketAnalysis: generatedPlan.market_analysis,
                          financialAnalysis: generatedPlan.financial_analysis,
                          riskAnalysis: generatedPlan.risk_analysis,
                          roadmap: generatedPlan.roadmap,
                          finalDecision: generatedPlan.message,
                        }),
                      });

                      const data = await response.json();

                      if (!response.ok) {
                        throw new Error(data.detail || "Failed to save startup plan");
                      }

                      alert(data.message);
                    } catch (error) {
                      console.error(error);
                      alert("Unable to save the startup plan.");
                    }
                  }}
                >
                  💾 Save Startup Plan
                </button>
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
                <div className="chat-message-content">
                  <ReactMarkdown>{message.text}</ReactMarkdown>
                </div>
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