import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Profile.css";

export default function Profile() {
  const navigate = useNavigate();

  const [profile, setProfile] = useState({
    fullName: "Founder",
    skills: "",
    interests: "",
    experience: "",
    budget: "",
    goals: "",
  });

  const [saved, setSaved] = useState(false);
  useEffect(() => {
    const currentUserEmail = localStorage.getItem("currentUserEmail");

    if (!currentUserEmail) return;

    const users = JSON.parse(
      localStorage.getItem("startupUsers") || "{}"
    );

    const user = users[currentUserEmail];

    if (user?.profile) {
      setProfile(user.profile);
    }
  }, []);

  const handleChange = (e) => {
    setProfile({
      ...profile,
      [e.target.name]: e.target.value,
    });
    setSaved(false);
  };

  const handleSave = (e) => {
    e.preventDefault();

    const currentUserEmail = localStorage.getItem("currentUserEmail");

    if (!currentUserEmail) {
      alert("Please sign in first.");
      return;
    }

    const users = JSON.parse(
      localStorage.getItem("startupUsers") || "{}"
    );

    if (!users[currentUserEmail]) {
      alert("User account not found.");
      return;
    }

    users[currentUserEmail].profile = profile;

    localStorage.setItem(
      "startupUsers",
      JSON.stringify(users)
    );

    setSaved(true);
  };

  return (
    <div className="profile-page">
      <div className="profile-container">

        {/* Header */}
        <div className="profile-header">
          <div className="profile-top-nav">
            <div className="profile-nav-buttons">
              <button onClick={() => navigate("/home")}>
                Home
              </button>

              <button onClick={() => navigate("/dashboard")}>
                Dashboard
              </button>

              <button
                onClick={() => {
                  localStorage.removeItem("currentUserEmail");
                  navigate("/login");
                }}
              >
                Logout
              </button>
            </div>
          </div>

          <h1>User Profile</h1>
          <p>
            Tell us about yourself so your AI mentor can personalize your
            startup guidance.
          </p>
        </div>

        {/* Profile Form */}
        <form className="profile-card" onSubmit={handleSave}>

          <div className="profile-avatar">👤</div>

          <h2>User Information</h2>

          {/* Full Name */}
          <div className="profile-field">
            <label>Full Name</label>
            <input
              type="text"
              name="fullName"
              value={profile.fullName}
              onChange={handleChange}
              placeholder="Enter your name"
            />
          </div>

          {/* Skills */}
          <div className="profile-field">
            <label>Skills</label>
            <textarea
              name="skills"
              value={profile.skills}
              onChange={handleChange}
              placeholder="Example: Python, AI, Marketing, Design"
            />
          </div>

          {/* Interests */}
          <div className="profile-field">
            <label>Interests</label>
            <textarea
              name="interests"
              value={profile.interests}
              onChange={handleChange}
              placeholder="Example: AI, Education, Healthcare, Finance"
            />
          </div>

          {/* Experience */}
          <div className="profile-field">
            <label>Experience</label>
            <textarea
              name="experience"
              value={profile.experience}
              onChange={handleChange}
              placeholder="Describe your education, work, or project experience"
            />
          </div>

          {/* Budget */}
          <div className="profile-field">
            <label>Startup Budget</label>
            <select
              name="budget"
              value={profile.budget}
              onChange={handleChange}
            >
              <option value="">Select your budget</option>
              <option value="No Budget">No Budget</option>
              <option value="Under ₹10,000">Under ₹10,000</option>
              <option value="₹10,000 - ₹50,000">₹10,000 - ₹50,000</option>
              <option value="₹50,000 - ₹1 Lakh">₹50,000 - ₹1 Lakh</option>
              <option value="Above ₹1 Lakh">Above ₹1 Lakh</option>
            </select>
          </div>

          {/* Startup Goals */}
          <div className="profile-field">
            <label>Startup Goals</label>
            <textarea
              name="goals"
              value={profile.goals}
              onChange={handleChange}
              placeholder="Example: Build an MVP, validate my idea, launch a startup"
            />
          </div>

          {/* Save */}
          <button type="submit" className="save-profile-button">
            💾 Save Founder Profile
          </button>

          {saved && (
            <p className="profile-success">
              ✓ Profile saved successfully!
            </p>
          )}

        </form>

        {/* Navigation */}
        <div className="profile-actions">
          <button onClick={() => navigate("/dashboard")}>
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