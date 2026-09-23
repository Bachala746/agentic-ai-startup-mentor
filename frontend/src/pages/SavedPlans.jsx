import { useEffect, useState } from "react";

export default function SavedPlans() {
  const [savedPlans, setSavedPlans] = useState([]);
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
              {new Date(plan.created_at).toLocaleString()}
            </p>
          </div>
        ))
      )}
    </div>
  );
}