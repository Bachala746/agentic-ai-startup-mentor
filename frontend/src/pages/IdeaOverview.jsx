import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./IdeaOverview.css";

export default function IdeaOverview() {
  const navigate = useNavigate();

  const startupIdea =
    localStorage.getItem("selectedStartupIdea") || "";

  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Generate startup overview
  const generateOverview = async () => {
    setLoading(true);
    setError("");
    setOverview(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/idea-overview",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            startupIdea: startupIdea,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        const backendMessage =
          typeof data.detail === "object"
            ? data.detail.message
            : data.detail;

        throw new Error(
          backendMessage ||
            "Unable to generate startup overview."
        );
      }

      setOverview(data);
    } catch (err) {
      console.error("Idea overview error:", err);

      if (err instanceof TypeError) {
        setError(
          "🌐 Unable to connect to the AI service. Please check that the backend is running."
        );
      } else {
        setError(
          err.message ||
            "Unable to generate the startup overview right now."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  // Automatically generate overview when page opens
  useEffect(() => {
    if (!startupIdea) {
      setLoading(false);
      return;
    }

    generateOverview();
  }, [startupIdea]);

  const handleDetailedAnalysis = () => {
    navigate("/dashboard");
  };

  // No startup idea
  if (!startupIdea) {
    return (
      <div className="idea-overview-page">
        <div className="idea-overview-card">
          <h1>No Startup Idea Selected</h1>

          <p>
            Please go back and select a startup idea first.
          </p>

          <button
            className="overview-back-btn"
            onClick={() => navigate("/")}
          >
            ← Choose Startup Idea
          </button>
        </div>
      </div>
    );
  }

  // Loading
  if (loading) {
    return (
      <div className="idea-overview-page">
        <div className="idea-overview-card loading-card">
          <div className="overview-label">
            STARTUP IDEA OVERVIEW
          </div>

          <h1>Understanding Your Startup Idea...</h1>

          <p>
            AI is preparing a quick overview specifically
            for your startup idea.
          </p>

          <div className="loading-text">
            ✨ Generating startup overview...
          </div>
        </div>
      </div>
    );
  }

  // Error
  if (error || !overview) {
    return (
      <div className="idea-overview-page">
        <div className="idea-overview-card">
          <div className="overview-label">
            STARTUP IDEA OVERVIEW
          </div>

          <h1>{startupIdea}</h1>

          <p>{error}</p>

          <button
            className="overview-back-btn"
            onClick={generateOverview}
          >
            🔄 Try Again
          </button>

          <button
            className="overview-back-btn"
            onClick={() => navigate("/")}
          >
            ← Try Another Idea
          </button>
        </div>
      </div>
    );
  }

  // Successful overview
  return (
    <div className="idea-overview-page">
      <div className="idea-overview-card">

        <div className="overview-label">
          STARTUP IDEA OVERVIEW
        </div>

        <h1>{overview.title}</h1>

        <p className="overview-intro">
          A quick understanding of your startup idea before
          starting the detailed AI multi-agent analysis.
        </p>

        {/* Description */}
        <div className="overview-section full-width">
          <h3>💡 What is the idea?</h3>

          <p>{overview.description}</p>
        </div>

        {/* Problem + Users */}
        <div className="overview-grid">

          <div className="overview-section">
            <h3>🎯 Problem It Solves</h3>

            <ul>
              {overview.problem.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="overview-section">
            <h3>👥 Target Users</h3>

            <ul>
              {overview.target_users.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>

        </div>

        {/* Features + How it works */}
        <div className="overview-grid">

          <div className="overview-section">
            <h3>⚙️ Key Features</h3>

            <ul>
              {overview.key_features.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="overview-section">
            <h3>🔄 How It Works</h3>

            <ol>
              {overview.how_it_works.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ol>
          </div>

        </div>

        {/* First Steps */}
        <div className="overview-section full-width">
          <h3>🚀 What Should You Do First?</h3>

          <ol>
            {overview.first_steps.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ol>
        </div>

        {/* Opportunity + Challenges */}
        <div className="overview-grid">

          <div className="overview-section">
            <h3>📈 Opportunity</h3>

            <p>{overview.opportunity}</p>
          </div>

          <div className="overview-section">
            <h3>⚠️ Challenges</h3>

            <ul>
              {overview.challenges.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>

        </div>

        {/* Continue */}
        <div className="overview-action">

          <p>
            Ready for the detailed Market, Finance, Risk
            and Decision analysis?
          </p>

          <button
            className="detailed-analysis-btn"
            onClick={handleDetailedAnalysis}
          >
            🚀 Analyze This Idea in Detail
          </button>

        </div>

      </div>
    </div>
  );
}