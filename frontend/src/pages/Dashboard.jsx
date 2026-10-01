import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import "./Dashboard.css";

export default function Dashboard() {
  const navigate = useNavigate();

  const [founderProfile, setFounderProfile] = useState(null);
  const [startupIdea, setStartupIdea] = useState("");
  const [selectedMentor, setSelectedMentor] =
    useState("Strategy Mentor");

  const [generatedPlan, setGeneratedPlan] = useState(null);
  const [completedSteps, setCompletedSteps] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const [chatMessage, setChatMessage] = useState("");

  const [chatHistory, setChatHistory] = useState([
    {
      sender: "AI",
      text: "Hi Founder! I'm ready to help you build your startup.",
    },
  ]);

  useEffect(() => {
    const currentUserEmail =
      localStorage.getItem("currentUserEmail");

    if (currentUserEmail) {
      try {
        const users = JSON.parse(
          localStorage.getItem("startupUsers") || "{}"
        );

        const user = users[currentUserEmail];

        if (user?.profile) {
          setFounderProfile(user.profile);
        }
      } catch (error) {
        console.error(
          "Unable to load user profile:",
          error
        );
      }
    }

    const savedStartupIdea =
      localStorage.getItem("selectedStartupIdea");

    if (savedStartupIdea) {
      setStartupIdea(savedStartupIdea);
    }

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
      description:
        "Business strategy & market planning",
    },
    {
      name: "Pitch Deck Coach",
      icon: "📊",
      description:
        "Pitch preparation & investor guidance",
    },
    {
      name: "Tech Architect",
      icon: "⚙️",
      description:
        "Technology & product architecture",
    },
  ];

  const handleGenerate = async (event) => {
    event.preventDefault();

    if (!startupIdea.trim()) {
      alert("Please enter your startup idea first!");
      return;
    }

    setIsGenerating(true);
    setGeneratedPlan(null);
    setCompletedSteps([]);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/startup-plan",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            startupIdea,
            founderProfile,
            mentor: selectedMentor,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Failed to generate startup plan."
        );
      }

      setGeneratedPlan(data);
    } catch (error) {
      console.error(
        "Startup plan error:",
        error
      );

      alert(
        error.message ||
          "Unable to generate the startup plan."
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSendMessage = async (event) => {
    event.preventDefault();

    if (!chatMessage.trim()) {
      return;
    }

    const userMessage = chatMessage;

    setChatHistory((previous) => [
      ...previous,
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
            startupIdea,
            mentor: selectedMentor,
            founderProfile,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Chat request failed."
        );
      }

      setChatHistory((previous) => [
        ...previous,
        {
          sender: "AI",
          text: data.reply,
        },
      ]);
    } catch (error) {
      console.error(
        "Mentor chat error:",
        error
      );

      setChatHistory((previous) => [
        ...previous,
        {
          sender: "AI",
          text:
            "Sorry, I could not connect to the AI mentor right now.",
        },
      ]);
    }
  };

  const toggleRoadmapStep = async (index) => {
    const newProgress = completedSteps.includes(index)
      ? completedSteps.filter(
          (item) => item !== index
        )
      : [...completedSteps, index];

    setCompletedSteps(newProgress);

    if (!generatedPlan?.id) {
      return;
    }

    try {
      await fetch(
        "http://127.0.0.1:8000/update-roadmap-progress",
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            planId: generatedPlan.id,
            completedSteps: newProgress,
          }),
        }
      );
    } catch (error) {
      console.error(
        "Roadmap progress error:",
        error
      );
    }
  };

  const saveStartupPlan = async () => {
    if (!generatedPlan) {
      return;
    }

    try {
      const currentUserEmail =
        localStorage.getItem(
          "currentUserEmail"
        ) || "";

      const response = await fetch(
        "http://127.0.0.1:8000/save-plan",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            userEmail: currentUserEmail,
            startupIdea,
            mentor: selectedMentor,
            marketAnalysis:
              generatedPlan.market_analysis || {},
            financialAnalysis:
              generatedPlan.financial_analysis || {},
            riskAnalysis:
              generatedPlan.risk_analysis || {},
            roadmap:
              generatedPlan.roadmap || [],
            roadmapProgress:
              completedSteps,
            finalDecision:
              generatedPlan.message || "",
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Failed to save startup plan."
        );
      }

      alert(data.message);

      setGeneratedPlan((previous) => ({
        ...previous,
        id: data.planId,
      }));
    } catch (error) {
      console.error(
        "Save plan error:",
        error
      );

      alert(
        error.message ||
          "Unable to save the startup plan."
      );
    }
  };

  const renderList = (items) => {
    if (!Array.isArray(items) || items.length === 0) {
      return <p>Not available</p>;
    }

    return (
      <ul>
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    );
  };

  const renderCompetitors = (items) => {
    if (!Array.isArray(items) || items.length === 0) {
      return <p>Not available</p>;
    }

    return (
      <div className="competitor-list">
        {items.map((competitor, index) => {
          const name =
            typeof competitor === "string"
              ? competitor
              : competitor?.name || "Unknown competitor";

          const description =
            typeof competitor === "object" && competitor?.description
              ? competitor.description
              : "Description not available.";

          return (
            <div
              className="competitor-item"
              key={`${name}-${index}`}
            >
              <strong>{name}</strong>
              <p>{description}</p>
            </div>
          );
        })}
      </div>
    );
  };

  const renderWebSources = (category) => {
    const sources =
      generatedPlan?.web_sources?.filter(
        (source) =>
          source.category === category
      ) || [];

    if (sources.length === 0) {
      return (
        <p>
          No current web sources available.
        </p>
      );
    }

    return (
      <div className="web-source-list">
        {sources.map((source, index) => (
          <div
            className="web-source-item"
            key={`${category}-${index}`}
          >
            <strong>
              {source.title ||
                "Web Research Result"}
            </strong>

            <p>
              <strong>Source:</strong>{" "}
              {source.url
                ? (() => {
                    try {
                      return new URL(
                        source.url
                      ).hostname;
                    } catch {
                      return "Web Source";
                    }
                  })()
                : "Web Source"}
            </p>

              {source.snippet && (
                <p>
                  {source.snippet.length > 250
                    ? `${source.snippet.slice(0, 250)}...`
                    : source.snippet}
                </p>
              )}

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
    );
  };

  return (
    <div className="dashboard-page">
      <div className="dashboard-container">

        {/* ================= HEADER ================= */}

        <header className="dashboard-header">
          <div>
            <h2>🚀 AI Startup Mentor</h2>
            <span>Founder Workspace</span>
          </div>

          <div className="dashboard-nav">
            <button
              onClick={() =>
                navigate("/home")
              }
            >
              Home
            </button>

            <button
              onClick={() =>
                navigate("/profile")
              }
            >
              Profile
            </button>

            <button
              className="logout-btn"
              onClick={() => {
                localStorage.removeItem(
                  "currentUserEmail"
                );

                navigate("/login");
              }}
            >
              Logout
            </button>
          </div>
        </header>

        {/* ================= WELCOME ================= */}

        <section className="welcome-card">
          <div>
            <span className="welcome-label">
              YOUR AI CO-FOUNDER
            </span>

            <h1>
              Welcome back{" "}
              {founderProfile?.fullName ||
                "Startup Builder"}{" "}
              👋
            </h1>

            <p>
              Turn your idea into a personalized
              startup plan.
            </p>
          </div>

          <div className="status">
            <span></span>
            AI Mentor Online
          </div>
        </section>

        {/* ================= USER PROFILE ================= */}

        {founderProfile && (
          <section className="founder-summary">
            <div>
              <span>SKILLS</span>

              <strong>
                {founderProfile.skills ||
                  "Not provided"}
              </strong>
            </div>

            <div>
              <span>INTERESTS</span>

              <strong>
                {founderProfile.interests ||
                  "Not provided"}
              </strong>
            </div>

            <div>
              <span>BUDGET</span>

              <strong>
                {founderProfile.budget ||
                  "Not provided"}
              </strong>
            </div>

            <div>
              <span>GOALS</span>

              <strong>
                {founderProfile.goals ||
                  "Not provided"}
              </strong>
            </div>
          </section>
        )}

        {/* ================= INPUT AREA ================= */}

        <div className="workspace-grid">

          {/* Startup Idea */}

          <section className="dashboard-card idea-card">
            <div className="card-heading">
              <div className="card-icon">
                💡
              </div>

              <div>
                <h2>Startup Idea</h2>
                <p>
                  What are you building?
                </p>
              </div>
            </div>

            <form
              onSubmit={handleGenerate}
            >
              <textarea
                value={startupIdea}
                onChange={(event) =>
                  setStartupIdea(
                    event.target.value
                  )
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
              <div className="card-icon">
                🤖
              </div>

              <div>
                <h2>
                  Choose Your Mentor
                </h2>

                <p>
                  Select the guidance you need
                </p>
              </div>
            </div>

            <div className="mentor-grid">
              {mentors.map((mentor) => (
                <button
                  key={mentor.name}
                  type="button"
                  className={`mentor-option ${
                    selectedMentor ===
                    mentor.name
                      ? "selected"
                      : ""
                  }`}
                  onClick={() =>
                    setSelectedMentor(
                      mentor.name
                    )
                  }
                >
                  <span className="mentor-icon">
                    {mentor.icon}
                  </span>

                  <strong>
                    {mentor.name}
                  </strong>

                  <small>
                    {mentor.description}
                  </small>
                </button>
              ))}
            </div>
          </section>
        </div>

        {/* ================= GENERATED PLAN ================= */}

        {generatedPlan && (
          <section className="dashboard-card results-card">

            <div className="card-heading">
              <div className="card-icon">
                🧠
              </div>

              <div>
                <h2>
                  AI Startup Analysis
                </h2>

                <p>
                  Generated by your
                  multi-agent system
                </p>
              </div>
            </div>

            {/* ================= MARKET ANALYSIS ================= */}

            <div className="result-section">
              <h3>📊 Market Analysis</h3>

              <div className="analysis-item">
                <h4>Target Customers</h4>
                {renderList(
                  generatedPlan.market_analysis?.target_customers
                )}
              </div>

              <div className="analysis-item">
                <h4>Customer Problem</h4>
                <p>
                  {generatedPlan.market_analysis?.customer_problem ||
                    "Not available"}
                </p>
              </div>

              <div className="analysis-item">
                <h4>Market Demand</h4>
                <p>
                  {generatedPlan.market_analysis?.market_demand ||
                    "Not available"}
                </p>
              </div>

              <div className="analysis-item">
                <h4>Opportunities</h4>
                {renderList(
                  generatedPlan.market_analysis?.opportunities
                )}
              </div>

              <div className="analysis-item">
                <h4>🌐 Market Trends</h4>
                {renderWebSources("Market Trends")}
              </div>
            </div>

            {/* ================= COMPETITORS / ALTERNATIVES ================= */}

            <div className="result-section">
              <h3>🏢 Competitors / Alternatives</h3>

              <div className="analysis-item">
                {renderCompetitors(
                  generatedPlan.market_analysis?.competitors_or_alternatives ||
                    generatedPlan.market_analysis?.competitors
                )}
              </div>

              <div className="analysis-item">
                <h4>🌐 Competitors & Alternatives</h4>
                {renderWebSources("Competitors & Alternatives")}
              </div>
            </div>

            {/* ================= OTHER MARKET ANALYSIS ================= */}

            <div className="result-section">
              <h3>💡 Other Market Analysis</h3>

              <div className="analysis-item">
                <h4>Market Gaps</h4>
                {renderList(
                  generatedPlan.market_analysis?.market_gaps
                )}
              </div>

              <div className="analysis-item">
                <h4>Key Insights</h4>
                {renderList(
                  generatedPlan.market_analysis?.market_insights
                )}
              </div>

              <div className="analysis-item">
                <h4>🌐 Recent Developments</h4>
                {renderWebSources("Recent Developments")}
              </div>
            </div>

            {/* ================= FINANCIAL ANALYSIS ================= */}

            <div className="result-section">
              <h3>
                💰 Financial Analysis
              </h3>

              <div className="analysis-item">
                <h4>
                  Financial Practicality
                </h4>

                <p>
                  {generatedPlan
                    .financial_analysis
                    ?.financial_practicality ||
                    "Not available"}
                </p>
              </div>

              <div className="analysis-item">
                <h4>
                  Expense Categories
                </h4>

                {renderList(
                  generatedPlan
                    .financial_analysis
                    ?.expense_categories
                )}
              </div>

              <div className="analysis-item">
                <h4>
                  Low-Cost MVP
                </h4>

                {renderList(
                  generatedPlan
                    .financial_analysis
                    ?.low_cost_mvp
                )}
              </div>

              <div className="analysis-item">
                <h4>
                  Revenue Models
                </h4>

                {renderList(
                  generatedPlan
                    .financial_analysis
                    ?.revenue_models
                )}
              </div>

              <div className="analysis-item">
                <h4>
                  Financial Constraints
                </h4>

                {renderList(
                  generatedPlan
                    .financial_analysis
                    ?.financial_constraints
                )}
              </div>

              <div className="analysis-item">
                <h4>
                  Recommendations
                </h4>

                {renderList(
                  generatedPlan
                    .financial_analysis
                    ?.recommendations
                )}
              </div>
            </div>

            {/* ================= RISK ANALYSIS ================= */}

            <div className="result-section">
              <h3>
                ⚠️ Risk Analysis
              </h3>

              <div className="analysis-item">
                <h4>
                  Market Risks
                </h4>

                {renderList(
                  generatedPlan
                    .risk_analysis
                    ?.market_risks
                )}
              </div>

              <div className="analysis-item">
                <h4>
                  Financial Risks
                </h4>

                {renderList(
                  generatedPlan
                    .risk_analysis
                    ?.financial_risks
                )}
              </div>

              <div className="analysis-item">
                <h4>
                  Product & Technical Risks
                </h4>

                {renderList(
                  generatedPlan
                    .risk_analysis
                    ?.product_technical_risks
                )}
              </div>

              <div className="analysis-item">
                <h4>
                  Customer Adoption Risks
                </h4>

                {renderList(
                  generatedPlan
                    .risk_analysis
                    ?.customer_adoption_risks
                )}
              </div>

              <div className="analysis-item">
                <h4>
                  Implementation Challenges
                </h4>

                {renderList(
                  generatedPlan
                    .risk_analysis
                    ?.implementation_challenges
                )}
              </div>

              <div className="analysis-item">
                <h4>
                  Mitigation Strategies
                </h4>

                {renderList(
                  generatedPlan
                    .risk_analysis
                    ?.mitigation_strategies
                )}
              </div>
            </div>

            {/* ================= ROADMAP ================= */}

            <div className="result-section">
              <h3>
                🛣️ Startup Roadmap
              </h3>

              {Array.isArray(
                generatedPlan.roadmap
              ) &&
              generatedPlan.roadmap.length > 0 ? (
                <ol>
                  {generatedPlan.roadmap.map(
                    (step, index) => (
                      <li
                        key={index}
                        style={{
                          marginBottom: "10px",
                        }}
                      >
                        <label
                          style={{
                            cursor: "pointer",
                          }}
                        >
                          <input
                            type="checkbox"
                            checked={completedSteps.includes(
                              index
                            )}
                            onChange={() =>
                              toggleRoadmapStep(
                                index
                              )
                            }
                          />

                          <span
                            style={{
                              marginLeft:
                                "10px",
                            }}
                          >
                            {step}
                          </span>
                        </label>
                      </li>
                    )
                  )}
                </ol>
              ) : (
                <p>
                  Roadmap not available.
                </p>
              )}
            </div>

            {/* ================= FINAL DECISION ================= */}

            <div className="result-section">
              <h3>
                🎯 Final Decision
              </h3>

              <p>
                {generatedPlan.message ||
                  "No final decision generated."}
              </p>
            </div>

            {/* ================= SAVE ================= */}

            <div className="save-plan-container">
              <button
                className="save-plan-btn"
                onClick={saveStartupPlan}
              >
                💾 Save Startup Plan
              </button>
            </div>

            {/* ================= ACTIVE MENTOR ================= */}

            <section className="selected-mentor">
              <span>
                ACTIVE MENTOR
              </span>

              <strong>
                {selectedMentor}
              </strong>

              <p>
                Your selected AI mentor will
                use your user profile when
                providing guidance.
              </p>
            </section>

         </section>
        )}
        {/* ================= AI MENTOR CHAT ================= */}

        <section className="dashboard-card chat-card">
          <div className="card-heading">
            <div className="card-icon">
              💬
            </div>

            <div>
              <h2>
                AI Mentor Chat
              </h2>

              <p>
                Ask questions about your startup
              </p>
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
                <strong>
                  {message.sender}
                </strong>

                <div className="chat-message-content">
                  <ReactMarkdown>
                    {message.text}
                  </ReactMarkdown>
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
              onChange={(event) =>
                setChatMessage(event.target.value)
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