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
          <li key={index}>{item}</li>
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
            className={window.location.pathname === "/home" ? "saved-active-nav" : ""}
            onClick={() => navigate("/home")}
          >
            💡 Startup Workspace
          </button>

          <button
            onClick={() => navigate("/dashboard")}
          >
            🏠 Dashboard
          </button>

          <button
            className="saved-active-nav"
            onClick={() => navigate("/saved-plans")}
          >
            💾 Saved Plans
          </button>

          <button
            onClick={() => navigate("/agent-insights")}
          >
            📊 Agent Insights
          </button>

          <button
            onClick={() => navigate("/profile")}
          >
            ⚙️ User Profile
          </button>

        </nav>

        <div className="saved-sidebar-bottom">

          <button onClick={handleLogout}>
            📕 Logout
          </button>

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
              <div className="saved-state-icon">
                ⏳
              </div>

              <h2>Loading Saved Plans</h2>

              <p>
                Please wait while we load your startup plans.
              </p>
            </div>
          )}

          {/* Empty */}
          {!isLoading && savedPlans.length === 0 && (
            <div className="saved-state-card">

              <div className="saved-state-icon">
                💡
              </div>

              <h2>No Saved Plans Yet</h2>

              <p>
                Generate a startup plan from the Dashboard
                and save it here for future reference.
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
                    {savedPlans.length === 1
                      ? "plan"
                      : "plans"}
                  </p>
                </div>

              </div>

              <div className="saved-plans-list">

                {savedPlans.map((plan) => (
                  <article
                    className="saved-plan-card"
                    key={plan.id}
                  >

                    <div className="saved-plan-top">

                      <div className="saved-plan-icon">
                        🚀
                      </div>

                      <div className="saved-plan-title-area">

                        <h2>
                          {plan.startup_idea}
                        </h2>

                        <p>
                          Your personalized startup analysis
                          generated by the AI mentor system.
                        </p>

                      </div>

                    </div>

                    <div className="saved-plan-meta">

                      <div>
                        <span>MENTOR</span>
                        <strong>
                          {plan.mentor}
                        </strong>
                      </div>

                      <div>
                        <span>SAVED</span>
                        <strong>
                          {formatSavedDate(
                            plan.created_at
                          )}
                        </strong>
                      </div>

                    </div>

                    <div className="saved-plan-actions">

                      <button
                        className="saved-view-btn"
                        onClick={() =>
                          setSelectedPlan(plan)
                        }
                      >
                        👁️ View Full Plan
                      </button>

                      <button
                        className="saved-delete-btn"
                        onClick={() =>
                          handleDeletePlan(plan.id)
                        }
                      >
                        🗑️ Delete Plan
                      </button>

                    </div>

                  </article>
                ))}

              </div>

              <div className="saved-plans-info">
                💡 You can save unlimited startup plans. Keep
                your ideas organized and delete any plan whenever
                you no longer need it.
              </div>
            </>
          )}

        </section>

      </main>

      {/* ================= FULL PLAN MODAL ================= */}
      {selectedPlan && (
        <div className="saved-modal-overlay">

          <div className="saved-modal">

            <div className="saved-modal-header">

              <div>
                <span className="saved-modal-label">
                  STARTUP PLAN
                </span>

                <h1>
                  {selectedPlan.startup_idea}
                </h1>

                <p>
                  Mentor: {selectedPlan.mentor}
                </p>
              </div>

              <button
                className="saved-modal-close"
                onClick={() =>
                  setSelectedPlan(null)
                }
              >
                ✕
              </button>

            </div>

            {/* Market Analysis */}
            <section className="saved-detail-section">

              <div className="saved-detail-heading">
                <span>📊</span>
                <h2>Market Analysis</h2>
              </div>

              <h3>Target Customers</h3>
              {renderList(
                selectedPlan.market_analysis
                  ?.target_customers
              )}

              <h3>Customer Problem</h3>
              <p>
                {selectedPlan.market_analysis
                  ?.customer_problem ||
                  "Not available"}
              </p>

              <h3>Market Demand</h3>
              <p>
                {selectedPlan.market_analysis
                  ?.market_demand ||
                  "Not available"}
              </p>

              <h3>Opportunities</h3>
              {renderList(
                selectedPlan.market_analysis
                  ?.opportunities
              )}

              <h3>Competitors / Alternatives</h3>
              {renderList(
                selectedPlan.market_analysis
                  ?.competitors_or_alternatives
              )}

              <h3>Market Gaps</h3>
              {renderList(
                selectedPlan.market_analysis
                  ?.market_gaps
              )}

              <h3>Key Insights</h3>
              {renderList(
                selectedPlan.market_analysis
                  ?.market_insights
              )}

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
                  ?.financial_practicality ||
                  "Not available"}
              </p>

              <h3>Expense Categories</h3>
              {renderList(
                selectedPlan.financial_analysis
                  ?.expense_categories
              )}

              <h3>Low-Cost MVP</h3>
              <p>
                {selectedPlan.financial_analysis
                  ?.low_cost_mvp ||
                  "Not available"}
              </p>

              <h3>Revenue Models</h3>
              {renderList(
                selectedPlan.financial_analysis
                  ?.revenue_models
              )}

              <h3>Financial Constraints</h3>
              {renderList(
                selectedPlan.financial_analysis
                  ?.financial_constraints
              )}

              <h3>Recommendations</h3>
              {renderList(
                selectedPlan.financial_analysis
                  ?.recommendations
              )}

            </section>

            {/* Risk Analysis */}
            <section className="saved-detail-section">

              <div className="saved-detail-heading">
                <span>⚠️</span>
                <h2>Risk Analysis</h2>
              </div>

              <h3>Market Risks</h3>
              {renderList(
                selectedPlan.risk_analysis
                  ?.market_risks
              )}

              <h3>Financial Risks</h3>
              {renderList(
                selectedPlan.risk_analysis
                  ?.financial_risks
              )}

              <h3>Product / Technical Risks</h3>
              {renderList(
                selectedPlan.risk_analysis
                  ?.product_technical_risks
              )}

              <h3>Customer Adoption Risks</h3>
              {renderList(
                selectedPlan.risk_analysis
                  ?.customer_adoption_risks
              )}

              <h3>Implementation Challenges</h3>
              {renderList(
                selectedPlan.risk_analysis
                  ?.implementation_challenges
              )}

              <h3>Mitigation Strategies</h3>
              {renderList(
                selectedPlan.risk_analysis
                  ?.mitigation_strategies
              )}

            </section>

            {/* Roadmap */}
            <section className="saved-detail-section">

              <div className="saved-detail-heading">
                <span>🗺️</span>
                <h2>Startup Roadmap</h2>
              </div>

              {renderList(selectedPlan.roadmap)}

            </section>

            {/* Final Decision */}
            <section className="saved-detail-section saved-final-section">

              <div className="saved-detail-heading">
                <span>🎯</span>
                <h2>Final Decision</h2>
              </div>

              <p>
                {selectedPlan.final_decision ||
                  "Not available"}
              </p>

            </section>

            <div className="saved-modal-footer">

              <button
                className="saved-close-btn"
                onClick={() =>
                  setSelectedPlan(null)
                }
              >
                Close Plan
              </button>

            </div>

          </div>

        </div>
      )}

    </div>
  );
}