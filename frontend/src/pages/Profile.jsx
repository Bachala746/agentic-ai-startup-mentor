import { useNavigate } from "react-router-dom";
import "./Profile.css";

export default function Profile() {
  const navigate = useNavigate();

  return (
    <div className="profile-page">

      <div className="profile-container">

        {/* Header */}
        <div className="profile-header">
          <button
            className="back-button"
            onClick={() => navigate("/home")}
          >
            ← Back to Startup Mentor
          </button>

          <h1>Founder Profile</h1>
          <p>Manage your startup mentor profile and preferences.</p>
        </div>

        {/* Profile Card */}
        <div className="profile-card">

          <div className="profile-avatar">
            👤
          </div>

          <h2>Founder</h2>
          <p className="profile-role">Startup Explorer</p>

          <div className="profile-details">

            <div className="profile-detail">
              <span>Full Name</span>
              <strong>Founder</strong>
            </div>

            <div className="profile-detail">
              <span>Role</span>
              <strong>Startup Founder</strong>
            </div>

            <div className="profile-detail">
              <span>Preferred Mentor</span>
              <strong>Strategy Mentor</strong>
            </div>

            <div className="profile-detail">
              <span>Account Status</span>
              <strong className="status">● Active</strong>
            </div>

          </div>

        </div>

        {/* Startup Stats */}
        <div className="profile-section">

          <h2>Your Startup Journey</h2>

          <div className="profile-stats">

            <div className="stat-card">
              <span>💡</span>
              <strong>0</strong>
              <p>Startup Ideas</p>
            </div>

            <div className="stat-card">
              <span>📁</span>
              <strong>0</strong>
              <p>Saved Plans</p>
            </div>

            <div className="stat-card">
              <span>🤖</span>
              <strong>0</strong>
              <p>AI Sessions</p>
            </div>

          </div>

        </div>

        {/* Actions */}
        <div className="profile-actions">

          <button
            onClick={() => navigate("/dashboard")}
          >
            🚀 Go to Dashboard
          </button>

          <button
            className="logout-profile"
            onClick={() => navigate("/login")}
          >
            🚪 Logout
          </button>

        </div>

      </div>

    </div>
  );
}