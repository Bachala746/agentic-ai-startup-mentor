import { useEffect, useState } from "react";


function formatSavedDate(dateString) {
  const utcDate = new Date(dateString.replace(" ", "T") + "Z");

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

  return `${getPart("day")}/${getPart("month")}/${getPart("year")} ${getPart("hour")}:${getPart("minute")}:${getPart("second")} ${getPart("dayPeriod").toUpperCase()}`;
}


export default function SavedPlans() {
  const [savedPlans, setSavedPlans] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadSavedPlans = async () => {
      try {
        const userEmail =
          localStorage.getItem("currentUserEmail") || "";

        const response = await fetch(
          `http://127.0.0.1:8000/saved-plans?user_email=${encodeURIComponent(
            userEmail
          )}`
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error("Failed to load saved plans");
        }

        setSavedPlans(data.plans || []);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    loadSavedPlans();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: "30px", color: "white" }}>
        <h1>💾 Saved Startup Plans</h1>
        <p>Loading saved plans...</p>
      </div>
    );
  }

  if (selectedPlan) {
    return (
      <div style={{ padding: "30px", color: "white" }}>
        <button
          onClick={() => setSelectedPlan(null)}
          style={{
            marginBottom: "20px",
            padding: "10px 16px",
            borderRadius: "8px",
            border: "none",
            cursor: "pointer",
          }}
        >
          ← Back to Saved Plans
        </button>

        <h1>📋 Startup Plan Details</h1>

        <div
          style={{
            marginTop: "20px",
            padding: "20px",
            border: "1px solid #263352",
            borderRadius: "14px",
            background: "#0c1426",
          }}
        >
          <h2>{selectedPlan.startup_idea}</h2>
          <p>Mentor: {selectedPlan.mentor}</p>
          <p>
            Saved:{" "}
            {formatSavedDate(selectedPlan.created_at)}
          </p>
        </div>

        <div
          style={{
            marginTop: "20px",
            padding: "20px",
            border: "1px solid #263352",
            borderRadius: "14px",
            background: "#0c1426",
          }}
        >
          <h2>📊 Market Analysis</h2>

          {Object.entries(selectedPlan.market_analysis || {}).map(
            ([key, value]) => (
              <div key={key} style={{ marginTop: "12px" }}>
                <strong>
                  {key.replaceAll("_", " ")}
                </strong>
                <p>{String(value)}</p>
              </div>
            )
          )}
        </div>

        <div
          style={{
            marginTop: "20px",
            padding: "20px",
            border: "1px solid #263352",
            borderRadius: "14px",
            background: "#0c1426",
          }}
        >
          <h2>💰 Financial Analysis</h2>

          {Object.entries(selectedPlan.financial_analysis || {}).map(
            ([key, value]) => (
              <div key={key} style={{ marginTop: "12px" }}>
                <strong>
                  {key.replaceAll("_", " ")}
                </strong>
                <p>{String(value)}</p>
              </div>
            )
          )}
        </div>

        <div
          style={{
            marginTop: "20px",
            padding: "20px",
            border: "1px solid #263352",
            borderRadius: "14px",
            background: "#0c1426",
          }}
        >
          <h2>⚠️ Risk Analysis</h2>

          {Object.entries(selectedPlan.risk_analysis || {}).map(
            ([key, value]) => (
              <div key={key} style={{ marginTop: "12px" }}>
                <strong>
                  {key.replaceAll("_", " ")}
                </strong>
                <p>{String(value)}</p>
              </div>
            )
          )}
        </div>

        <div
          style={{
            marginTop: "20px",
            padding: "20px",
            border: "1px solid #263352",
            borderRadius: "14px",
            background: "#0c1426",
          }}
        >
          <h2>🗺️ Startup Roadmap</h2>

          <ol>
            {(selectedPlan.roadmap || []).map((step, index) => (
              <li key={index} style={{ marginBottom: "10px" }}>
                {step}
              </li>
            ))}
          </ol>
        </div>

        <div
          style={{
            marginTop: "20px",
            marginBottom: "30px",
            padding: "20px",
            border: "1px solid #263352",
            borderRadius: "14px",
            background: "#0c1426",
          }}
        >
          <h2>🎯 Final Decision</h2>
          <p>{selectedPlan.final_decision}</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: "30px", color: "white" }}>
      <h1>💾 Saved Startup Plans</h1>

      {savedPlans.length === 0 ? (
        <p>No saved startup plans yet.</p>
      ) : (
        savedPlans.map((plan) => (
          <div
            key={plan.id}
            style={{
              marginTop: "20px",
              padding: "20px",
              border: "1px solid #263352",
              borderRadius: "14px",
              background: "#0c1426",
            }}
          >
            <h2>{plan.startup_idea}</h2>

            <p>Mentor: {plan.mentor}</p>

            <p>
              Saved:{" "}
              {formatSavedDate(plan.created_at)}
            </p>

            <button
              onClick={() => setSelectedPlan(plan)}
              style={{
                marginTop: "10px",
                padding: "10px 18px",
                borderRadius: "8px",
                border: "none",
                cursor: "pointer",
              }}
            >
              👁️ View Full Plan
            </button>
          </div>
        ))
      )}
    </div>
  );
}