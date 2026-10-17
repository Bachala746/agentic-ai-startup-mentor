import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./SavedPlans.css";

function formatSavedDate(dateString) {
  if (!dateString) return "Date not available";

  const utcDate = new Date(
    dateString.replace(" ", "T") + "Z"
  );

  const parts = new Intl.DateTimeFormat("en-IN", {
    timeZone: "Asia/Kolkata",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  }).formatToParts(utcDate);

  const getPart = (type) =>
    parts.find((part) => part.type === type)?.value || "";

  return `${getPart("day")}/${getPart("month")}/${getPart(
    "year"
  )} ${getPart("hour")}:${getPart("minute")}:${getPart(
    "second"
  )} ${getPart("dayPeriod").toUpperCase()}`;
}

// Helper to safely parse both JSON strings and plain-text saved startup ideas
function parseStartupIdea(raw) {
  if (!raw) {
    return {
      title: "Untitled Startup Plan",
      description: "",
      problem: "",
      solution: "",
      usp: "",
      estimatedCost: "",
    };
  }

  // 1. Try parsing serialized JSON or direct object
  let obj = null;
  if (typeof raw === "object" && raw !== null) {
    obj = raw;
  } else if (typeof raw === "string") {
    const trimmed = raw.trim();
    if (
      (trimmed.startsWith("{") && trimmed.endsWith("}")) ||
      (trimmed.startsWith("[") && trimmed.endsWith("]"))
    ) {
      try {
        const parsed = JSON.parse(trimmed);
        obj = Array.isArray(parsed) ? parsed[0] : parsed;
      } catch {
        obj = null;
      }
    }
  }

  if (obj && typeof obj === "object") {
    return {
      title: obj.name || obj.title || "Startup Idea",
      description: obj.shortDescription || obj.description || "",
      problem: Array.isArray(obj.problem)
        ? obj.problem.join("; ")
        : obj.problem || "",
      solution: Array.isArray(obj.solution)
        ? obj.solution.join("; ")
        : obj.solution || "",
      usp: obj.usp || "",
      estimatedCost: obj.estimatedCost || obj.cost || obj.budget || "",
    };
  }

  // 2. Parse plain text (with or without labeled sections)
  const text = String(raw).trim();

  const stopPattern =
    "(?:\\n|\\r\\n)(?:Problem|Solution|USP|Differentiator|Estimated Cost|Est\\.|Cost|Budget|Difficulty|Why This Matches You|Founder Fit):|$";

  const getSection = (labelPattern) => {
    const regex = new RegExp(
      `(?:^|\\n|\\r\\n)(?:${labelPattern}):\\s*([\\s\\S]*?)(?=${stopPattern})`,
      "i"
    );
    const match = text.match(regex);
    return match ? match[1].trim() : "";
  };

  const problem = getSection("Problem|Customer Problem");
  const solution = getSection("Solution|Proposed Solution");
  const usp = getSection("USP|USP \\/ Differentiator|Differentiator");
  let estimatedCost = getSection(
    "Estimated Cost|Estimated Launch Cost|Est\\. Launch Cost|Cost|Budget"
  );

  if (!estimatedCost) {
    const pipeMatch = text.match(
      /(?:Estimated Cost|Est\. Launch Cost|Cost):\s*([^|\n\r]+)/i
    );
    if (pipeMatch) {
      estimatedCost = pipeMatch[1].trim();
    }
  }

  // Find start of labeled sections to extract title and short description
  const labelIndices = [
    text.search(/(?:^|\n|\r\n)(?:Problem|Customer Problem):/i),
    text.search(/(?:^|\n|\r\n)(?:Solution|Proposed Solution):/i),
    text.search(/(?:^|\n|\r\n)(?:USP|USP \/ Differentiator|Differentiator):/i),
    text.search(/(?:^|\n|\r\n)(?:Estimated Cost|Cost):/i),
  ].filter((idx) => idx !== -1);

  const firstSectionIdx =
    labelIndices.length > 0 ? Math.min(...labelIndices) : -1;
  const headerPart =
    firstSectionIdx !== -1 ? text.slice(0, firstSectionIdx).trim() : text.trim();

  let title = "";
  let description = "";

  const startupPrefixMatch = headerPart.match(
    /^Startup:\s*(.*?)(?:\n+Description:\s*([\s\S]*))?$/i
  );

  if (startupPrefixMatch) {
    title = startupPrefixMatch[1].trim();
    description = startupPrefixMatch[2] ? startupPrefixMatch[2].trim() : "";
  } else if (headerPart.includes(":")) {
    const colonIndex = headerPart.indexOf(":");
    if (colonIndex > 0 && colonIndex <= 60) {
      title = headerPart.slice(0, colonIndex).trim();
      description = headerPart.slice(colonIndex + 1).trim();
    } else {
      const lines = headerPart
        .split(/\r?\n/)
        .map((l) => l.trim())
        .filter(Boolean);
      title = lines[0] || "Startup Idea";
      description = lines.slice(1).join(" ");
    }
  } else {
    const lines = headerPart
      .split(/\r?\n/)
      .map((l) => l.trim())
      .filter(Boolean);
    if (lines.length > 1) {
      title = lines[0];
      description = lines.slice(1).join(" ");
    } else if (lines.length === 1) {
      if (headerPart.length > 80 && !problem && !solution) {
        const sentenceEnd = headerPart.search(/[.!?]\s/);
        if (sentenceEnd > 0 && sentenceEnd <= 80) {
          title = headerPart.slice(0, sentenceEnd + 1).trim();
          description = headerPart.slice(sentenceEnd + 1).trim();
        } else {
          title = headerPart.slice(0, 60).trim() + "...";
          description = headerPart;
        }
      } else {
        title = headerPart;
        description = "";
      }
    } else {
      title = "Startup Idea";
      description = "";
    }
  }

  // Clean markdown asterisks or hashes from title
  title = title.replace(/^[*#_\s]+|[*#_\s]+$/g, "");

  return {
    title: title || "Startup Idea",
    description,
    problem,
    solution,
    usp,
    estimatedCost,
  };
}

export default function SavedPlans() {
  const navigate = useNavigate();

  const [savedPlans, setSavedPlans] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const currentUserEmail =
    localStorage.getItem("currentUserEmail") || "";

  useEffect(() => {
    loadSavedPlans();
  }, []);

  const loadSavedPlans = async () => {
    try {
      setIsLoading(true);

      const response = await fetch(
        `http://127.0.0.1:8000/saved-plans?user_email=${encodeURIComponent(
          currentUserEmail
        )}`
      );

      if (!response.ok) {
        throw new Error("Failed to load saved plans");
      }

      const data = await response.json();

      setSavedPlans(data.plans || []);
    } catch (error) {
      console.error("Error loading saved plans:", error);
      setSavedPlans([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeletePlan = async (planId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this startup plan?"
    );

    if (!confirmed) return;

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/saved-plans/${planId}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to delete plan");
      }

      setSavedPlans((prevPlans) =>
        prevPlans.filter((plan) => plan.id !== planId)
      );

      if (selectedPlan?.id === planId) {
        setSelectedPlan(null);
      }
    } catch (error) {
      console.error("Delete plan error:", error);
      alert("Failed to delete the startup plan.");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("currentUserEmail");
    navigate("/login");
  };

  const renderList = (items) => {
    if (!items || items.length === 0) {
      return <p>Not available</p>;
    }

    return (
      <ul>
        {items.map((item, index) => (
          <li key={index}>
            {typeof item === "object" && item !== null
              ? item.name || item.description || JSON.stringify(item)
              : item}
          </li>
        ))}
      </ul>
    );
  };

  const renderRoadmap = (items, completedSteps = [], planId = null) => {
    if (!items || items.length === 0) {
      return <p>Not available</p>;
    }

    return (
      <ul>
        {items.map((item, index) => (
          <li key={index}>
            <input
              type="checkbox"
              checked={completedSteps.includes(index)}
              onChange={async () => {
                const newProgress = completedSteps.includes(index)
                  ? completedSteps.filter((step) => step !== index)
                  : [...completedSteps, index];

                try {
                  await fetch(
                    "http://127.0.0.1:8000/update-roadmap-progress",
                    {
                      method: "PUT",
                      headers: {
                        "Content-Type": "application/json",
                      },
                      body: JSON.stringify({
                        planId: planId,
                        completedSteps: newProgress,
                      }),
                    }
                  );

                  setSelectedPlan((previous) => ({
                    ...previous,
                    roadmap_progress: newProgress,
                  }));
                  setSavedPlans((previousPlans) =>
                    previousPlans.map((plan) =>
                      plan.id === planId
                        ? { ...plan, roadmap_progress: newProgress }
                        : plan
                    )
                  );
                } catch (error) {
                  console.error("Roadmap progress error:", error);
                }
              }}
            />

            <span style={{ marginLeft: "10px" }}>
              {typeof item === "object" && item !== null
                ? item.name || item.description || JSON.stringify(item)
                : item}
            </span>
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div className="saved-page">
      {/* ================= SIDEBAR ================= */}
      <aside className="saved-sidebar">
        <div className="saved-logo">
          <h2>AI Startup Mentor</h2>
        </div>

        <button
          className="saved-new-idea-btn"
          onClick={() => navigate("/home")}
        >
          + New Idea
        </button>

        <nav className="saved-sidebar-nav">
          <button
            className={
              window.location.pathname === "/home"
                ? "saved-active-nav"
                : ""
            }
            onClick={() => navigate("/home")}
          >
            💡 Startup Workspace
          </button>

          <button onClick={() => navigate("/dashboard")}>
            🏠 Dashboard
          </button>

          <button
            className="saved-active-nav"
            onClick={() => navigate("/saved-plans")}
          >
            💾 Saved Plans
          </button>

          <button onClick={() => navigate("/agent-insights")}>
            📊 Agent Insights
          </button>

          <button onClick={() => navigate("/profile")}>
            ⚙️ User Profile
          </button>
        </nav>

        <div className="saved-sidebar-bottom">
          <button onClick={handleLogout}>📕 Logout</button>
        </div>
      </aside>

      {/* ================= MAIN CONTENT ================= */}
      <main className="saved-main">
        {/* Header */}
        <header className="saved-header">
          <div>
            <h1>Saved Startup Plans</h1>
            <p>
              View, manage, and revisit your previously generated
              startup plans.
            </p>
          </div>

          <div className="saved-status">
            <span></span>
            Plans Stored
          </div>
        </header>

        {/* Main Content */}
        <section className="saved-content">
          {/* Loading */}
          {isLoading && (
            <div className="saved-state-card">
              <div className="saved-state-icon">⏳</div>
              <h2>Loading Saved Plans</h2>
              <p>Please wait while we load your startup plans.</p>
            </div>
          )}

          {/* Empty */}
          {!isLoading && savedPlans.length === 0 && (
            <div className="saved-state-card">
              <div className="saved-state-icon">💡</div>
              <h2>No Saved Plans Yet</h2>
              <p>
                Generate a startup plan from the Dashboard and save it here
                for future reference.
              </p>
              <button
                className="saved-primary-btn"
                onClick={() => navigate("/home")}
              >
                + Create New Startup Idea
              </button>
            </div>
          )}

          {/* Saved Plans */}
          {!isLoading && savedPlans.length > 0 && (
            <>
              <div className="saved-section-heading">
                <div>
                  <h2>Your Startup Plans</h2>
                  <p>
                    {savedPlans.length} saved{" "}
                    {savedPlans.length === 1 ? "plan" : "plans"}
                  </p>
                </div>
              </div>

              <div className="saved-plans-list">
                {savedPlans.map((plan) => {
                  const parsed = parseStartupIdea(plan.startup_idea);

                  return (
                    <article
                      className="saved-plan-card"
                      key={plan.id}
                    >
                      <div className="saved-plan-top">
                        <div className="saved-plan-icon">🚀</div>

                        <div className="saved-plan-title-area">
                          {/* 1. Startup Name as Card Heading */}
                          <h2>{parsed.title}</h2>

                          {/* 2. Short Description Below Title */}
                          {parsed.description ? (
                            <p className="saved-plan-desc">
                              {parsed.description}
                            </p>
                          ) : (
                            !parsed.problem &&
                            !parsed.solution && (
                              <p className="saved-plan-desc">
                                Your personalized startup analysis generated by
                                the AI mentor system.
                              </p>
                            )
                          )}

                          {/* 3. Labeled Sections: Problem, Solution, USP, Estimated Cost */}
                          {(parsed.problem ||
                            parsed.solution ||
                            parsed.usp ||
                            parsed.estimatedCost) && (
                            <div className="saved-plan-sections">
                              {parsed.problem && (
                                <div className="saved-plan-section-item">
                                  <span className="saved-plan-section-label">
                                    Problem
                                  </span>
                                  <p className="saved-plan-section-text">
                                    {parsed.problem}
                                  </p>
                                </div>
                              )}

                              {parsed.solution && (
                                <div className="saved-plan-section-item">
                                  <span className="saved-plan-section-label">
                                    Solution
                                  </span>
                                  <p className="saved-plan-section-text">
                                    {parsed.solution}
                                  </p>
                                </div>
                              )}

                              {(parsed.usp || parsed.estimatedCost) && (
                                <div className="saved-plan-section-row">
                                  {parsed.usp && (
                                    <div className="saved-plan-section-item">
                                      <span className="saved-plan-section-label">
                                        USP
                                      </span>
                                      <p className="saved-plan-section-text">
                                        {parsed.usp}
                                      </p>
                                    </div>
                                  )}

                                  {parsed.estimatedCost && (
                                    <div className="saved-plan-section-item">
                                      <span className="saved-plan-section-label">
                                        Estimated Cost
                                      </span>
                                      <p className="saved-plan-section-text saved-cost-text">
                                        {parsed.estimatedCost}
                                      </p>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="saved-plan-meta">
                        <div>
                          <span>MENTOR</span>
                          <strong>{plan.mentor}</strong>
                        </div>

                        <div>
                          <span>SAVED</span>
                          <strong>
                            {formatSavedDate(plan.created_at)}
                          </strong>
                        </div>
                      </div>

                      <div className="saved-plan-actions">
                        <button
                          className="saved-view-btn"
                          onClick={() => setSelectedPlan(plan)}
                        >
                          👁️ View Full Plan
                        </button>

                        <button
                          className="saved-delete-btn"
                          onClick={() => handleDeletePlan(plan.id)}
                        >
                          🗑️ Delete Plan
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>

              <div className="saved-plans-info">
                💡 You can save unlimited startup plans. Keep your ideas
                organized and delete any plan whenever you no longer need it.
              </div>
            </>
          )}
        </section>
      </main>

      {/* ================= FULL PLAN MODAL ================= */}
      {selectedPlan && (() => {
        const selectedParsed = parseStartupIdea(selectedPlan.startup_idea);

        return (
          <div className="saved-modal-overlay">
            <div className="saved-modal">
              <div className="saved-modal-header">
                <div>
                  <span className="saved-modal-label">STARTUP PLAN</span>

                  <h1>{selectedParsed.title}</h1>

                  {selectedParsed.description && (
                    <p className="saved-modal-desc">
                      {selectedParsed.description}
                    </p>
                  )}

                  <p>Mentor: {selectedPlan.mentor}</p>
                </div>

                <button
                  className="saved-modal-close"
                  onClick={() => setSelectedPlan(null)}
                >
                  ✕
                </button>
              </div>

              {/* Startup Concept Overview */}
              {(selectedParsed.problem ||
                selectedParsed.solution ||
                selectedParsed.usp ||
                selectedParsed.estimatedCost) && (
                <section className="saved-detail-section">
                  <div className="saved-detail-heading">
                    <span>💡</span>
                    <h2>Startup Concept Overview</h2>
                  </div>

                  {selectedParsed.problem && (
                    <>
                      <h3>Problem</h3>
                      <p>{selectedParsed.problem}</p>
                    </>
                  )}

                  {selectedParsed.solution && (
                    <>
                      <h3>Solution</h3>
                      <p>{selectedParsed.solution}</p>
                    </>
                  )}

                  {selectedParsed.usp && (
                    <>
                      <h3>USP</h3>
                      <p>{selectedParsed.usp}</p>
                    </>
                  )}

                  {selectedParsed.estimatedCost && (
                    <>
                      <h3>Estimated Cost</h3>
                      <p className="saved-cost-text">
                        {selectedParsed.estimatedCost}
                      </p>
                    </>
                  )}
                </section>
              )}

              {/* Market Analysis */}
              <section className="saved-detail-section">
                <div className="saved-detail-heading">
                  <span>📊</span>
                  <h2>Market Analysis</h2>
                </div>

                <h3>Target Customers</h3>
                {renderList(
                  selectedPlan.market_analysis?.target_customers
                )}

                <h3>Customer Problem</h3>
                <p>
                  {selectedPlan.market_analysis?.customer_problem ||
                    "Not available"}
                </p>

                <h3>Market Demand</h3>
                <p>
                  {selectedPlan.market_analysis?.market_demand ||
                    "Not available"}
                </p>

                <h3>Opportunities</h3>
                {renderList(selectedPlan.market_analysis?.opportunities)}

                <h3>Competitors / Alternatives</h3>
                {renderList(
                  selectedPlan.market_analysis
                    ?.competitors_or_alternatives
                )}

                <h3>Market Gaps</h3>
                {renderList(selectedPlan.market_analysis?.market_gaps)}

                <h3>Key Insights</h3>
                {renderList(selectedPlan.market_analysis?.market_insights)}
              </section>

              {/* Financial Analysis */}
              <section className="saved-detail-section">
                <div className="saved-detail-heading">
                  <span>💰</span>
                  <h2>Financial Analysis</h2>
                </div>

                <h3>Financial Practicality</h3>
                <p>
                  {selectedPlan.financial_analysis
                    ?.financial_practicality || "Not available"}
                </p>

                <h3>Expense Categories</h3>
                {renderList(
                  selectedPlan.financial_analysis?.expense_categories
                )}

                <h3>Low-Cost MVP</h3>
                <p>
                  {selectedPlan.financial_analysis?.low_cost_mvp ||
                    "Not available"}
                </p>

                <h3>Revenue Models</h3>
                {renderList(
                  selectedPlan.financial_analysis?.revenue_models
                )}

                <h3>Financial Constraints</h3>
                {renderList(
                  selectedPlan.financial_analysis?.financial_constraints
                )}

                <h3>Recommendations</h3>
                {renderList(
                  selectedPlan.financial_analysis?.recommendations
                )}
              </section>

              {/* Risk Analysis */}
              <section className="saved-detail-section">
                <div className="saved-detail-heading">
                  <span>⚠️</span>
                  <h2>Risk Analysis</h2>
                </div>

                <h3>Market Risks</h3>
                {renderList(selectedPlan.risk_analysis?.market_risks)}

                <h3>Financial Risks</h3>
                {renderList(selectedPlan.risk_analysis?.financial_risks)}

                <h3>Product / Technical Risks</h3>
                {renderList(
                  selectedPlan.risk_analysis?.product_technical_risks
                )}

                <h3>Customer Adoption Risks</h3>
                {renderList(
                  selectedPlan.risk_analysis?.customer_adoption_risks
                )}

                <h3>Implementation Challenges</h3>
                {renderList(
                  selectedPlan.risk_analysis?.implementation_challenges
                )}

                <h3>Mitigation Strategies</h3>
                {renderList(
                  selectedPlan.risk_analysis?.mitigation_strategies
                )}
              </section>

              {/* Roadmap */}
              <section className="saved-detail-section">
                <div className="saved-detail-heading">
                  <span>🗺️</span>
                  <h2>Startup Roadmap</h2>
                </div>

                {renderRoadmap(
                  selectedPlan.roadmap,
                  selectedPlan.roadmap_progress || [],
                  selectedPlan.id
                )}
              </section>

              {/* Final Decision */}
              <section className="saved-detail-section saved-final-section">
                <div className="saved-detail-heading">
                  <span>🎯</span>
                  <h2>Final Decision</h2>
                </div>

                <p>
                  {selectedPlan.final_decision || "Not available"}
                </p>
              </section>

              <div className="saved-modal-footer">
                <button
                  className="saved-update-btn"
                  onClick={() => {
                    alert("Plan updated successfully!");
                  }}
                >
                  💾 Update Plan
                </button>

                <button
                  className="saved-close-btn"
                  onClick={() => setSelectedPlan(null)}
                >
                  Close Plan
                </button>
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
}