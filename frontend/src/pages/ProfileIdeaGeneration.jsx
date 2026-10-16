import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./ProfileIdeaGeneration.css";

export default function ProfileIdeaGeneration() {
  const navigate = useNavigate();
  const location = useLocation();

  // 1. Skills
  const [selectedSkills, setSelectedSkills] = useState(["Full-Stack Web Dev", "AI & LLMs"]);
  const [customSkill, setCustomSkill] = useState("");

  // 2. Interests
  const [selectedInterests, setSelectedInterests] = useState(["B2B Productivity", "Creator Economy"]);
  const [customInterest, setCustomInterest] = useState("");

  // 3. Experience
  const [experienceLevel, setExperienceLevel] = useState("3 - 5 Years (Mid-level)");
  const [experienceSummary, setExperienceSummary] = useState("");

  // 4. Budget
  const [budget, setBudget] = useState("$1,000 - $10,000 (Bootstrapped)");

  // 5. Domain Knowledge
  const [selectedDomains, setSelectedDomains] = useState(["Software & SaaS", "E-Commerce"]);
  const [customDomain, setCustomDomain] = useState("");

  // 6. Startup Goals
  const [startupGoal, setStartupGoal] = useState("Profitable Cash-Flow Micro-SaaS");
  const [targetAudience, setTargetAudience] = useState("");

  // Submitting state
  const [isGenerating, setIsGenerating] = useState(false);

  // Preset Options
  const popularSkills = [
    "Full-Stack Web Dev",
    "AI & LLMs",
    "Mobile App Dev",
    "Product Design (UI/UX)",
    "B2B Sales & Outbound",
    "Growth Marketing & SEO",
    "Data Engineering",
    "Finance & Modeling",
  ];

  const popularInterests = [
    "B2B Productivity",
    "Creator Economy",
    "Health & Fitness",
    "FinTech & Payments",
    "EdTech & Upskilling",
    "Climate & CleanTech",
    "Autonomous AI Agents",
    "Gaming & Web3",
  ];

  const budgetOptions = [
    "$0 - $1,000 (Shoestring / Zero-Capital)",
    "$1,000 - $10,000 (Bootstrapped)",
    "$10,000 - $50,000 (Angel / Self-Funded)",
    "$50,000+ (Seeking VC / High-Capital)",
  ];

  const domainOptions = [
    "Software & SaaS",
    "E-Commerce & Retail",
    "Healthcare & Biotech",
    "Real Estate & PropTech",
    "Education & Academics",
    "Logistics & Supply Chain",
    "LegalTech",
    "Media & Entertainment",
  ];

  const goalOptions = [
    "Profitable Cash-Flow Micro-SaaS",
    "Fast-Growth Venture-Backed Unicorn",
    "Solo Founder / Indie Hacker Lifestyle",
    "AI Automation Agency to Product",
    "Social Impact / Mission-Driven Startup",
  ];

  const toggleSelection = (item, list, setList) => {
    if (list.includes(item)) {
      setList(list.filter((i) => i !== item));
    } else {
      setList([...list, item]);
    }
  };

  const addCustomItem = (value, list, setList, clearInput) => {
    const trimmed = value.trim();
    if (trimmed && !list.includes(trimmed)) {
      setList([...list, trimmed]);
      clearInput("");
    }
  };

  const handleGenerateIdeas = (e) => {
    e.preventDefault();
    setIsGenerating(true);

    const founderProfile = {
      skills: selectedSkills,
      interests: selectedInterests,
      experienceLevel,
      experienceSummary: experienceSummary.trim(),
      budget,
      domainKnowledge: selectedDomains,
      startupGoal,
      targetAudience: targetAudience.trim(),
    };

    // Save profile to local storage for downstream multi-agent workflows
    localStorage.setItem("founderProfile", JSON.stringify(founderProfile));

    // Simulation for UI feedback (connect to your backend endpoint when ready)
    setTimeout(() => {
      setIsGenerating(false);
      alert("Profile captured! Ready to trigger Gemini & LangGraph idea generation.");
      // Optional: navigate("/profile-ideas-result");
    }, 1200);
  };

  return (
    <div className="workspace-container">
      {/* Sidebar */}
      <aside className="workspace-sidebar">
        <div className="sidebar-header">
          <h2>AI Startup Mentor</h2>
          <button className="new-idea-btn" onClick={() => navigate("/home")}>
            ← Back to Home
          </button>
        </div>

        <nav className="sidebar-nav">
          <button
            className={`nav-item ${location.pathname === "/home" ? "active" : ""}`}
            onClick={() => navigate("/home")}
          >
            💡 Startup Workspace
          </button>

          <button className="nav-item" onClick={() => navigate("/dashboard")}>
            🏠 Dashboard
          </button>

          <button className="nav-item" onClick={() => navigate("/saved-plans")}>
            💾 Saved Plans
          </button>

          <button className="nav-item" onClick={() => navigate("/agent-insights")}>
            📊 Agent Insights
          </button>

          <button
            className={`nav-item ${
              location.pathname === "/profile-idea-generation" ? "active" : ""
            }`}
            onClick={() => navigate("/profile-idea-generation")}
          >
            🎯 Profile Idea Discovery
          </button>

          <button className="nav-item" onClick={() => navigate("/profile")}>
            ⚙️ User Profile
          </button>
        </nav>

        <div className="sidebar-footer">
          <button
            className="nav-item"
            onClick={() => {
              localStorage.removeItem("currentUserEmail");
              navigate("/login");
            }}
          >
            🚪 Logout
          </button>
        </div>
      </aside>

      {/* Main Workspace */}
      <main className="workspace-main">
        {/* Top Bar */}
        <header className="workspace-topbar">
          <div className="topbar-left">
            <h1>Founder Profile Discovery</h1>
            <p>Our Multi-Agent System analyzes your strengths to formulate viable startups</p>
          </div>

          <div className="topbar-right">
            <div className="agent-status purple-pulse">
              <span className="purple-status-dot"></span>
              Discovery Agents Online
            </div>

            <div className="user-profile-badge">Founder Mode</div>
          </div>
        </header>

        {/* Form Content */}
        <div className="workspace-content">
          <form className="profile-discovery-form" onSubmit={handleGenerateIdeas}>
            {/* Header Card */}
            <div className="profile-banner-card">
              <div className="banner-icon-badge">✨</div>
              <div>
                <h2>Tailor Ideas to Your Superpowers</h2>
                <p>
                  No startup idea yet? No problem. Provide your background, interests, and capital
                  constraints. Our AI agents will identify whitespace opportunities that match you.
                </p>
              </div>
            </div>

            {/* Grid Sections */}
            <div className="profile-sections-grid">
              {/* 1. Skills */}
              <div className="profile-section-card">
                <div className="section-header">
                  <span className="section-number">1</span>
                  <div>
                    <h3>Skills & Superpowers</h3>
                    <p>Select what you are good at (tech, design, growth, sales).</p>
                  </div>
                </div>

                <div className="chips-container">
                  {popularSkills.map((skill) => (
                    <button
                      type="button"
                      key={skill}
                      className={`profile-chip ${
                        selectedSkills.includes(skill) ? "chip-active" : ""
                      }`}
                      onClick={() => toggleSelection(skill, selectedSkills, setSelectedSkills)}
                    >
                      {skill} {selectedSkills.includes(skill) ? "✓" : "+"}
                    </button>
                  ))}
                </div>

                <div className="custom-input-group">
                  <input
                    type="text"
                    placeholder="Add other skill (e.g., SEO, DevOps)..."
                    value={customSkill}
                    onChange={(e) => setCustomSkill(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        addCustomItem(customSkill, selectedSkills, setSelectedSkills, setCustomSkill);
                      }
                    }}
                  />
                  <button
                    type="button"
                    className="add-chip-btn"
                    onClick={() =>
                      addCustomItem(customSkill, selectedSkills, setSelectedSkills, setCustomSkill)
                    }
                  >
                    Add
                  </button>
                </div>
              </div>

              {/* 2. Interests */}
              <div className="profile-section-card">
                <div className="section-header">
                  <span className="section-number">2</span>
                  <div>
                    <h3>Passions & Curiosities</h3>
                    <p>What spaces, industries, or trends excite you most?</p>
                  </div>
                </div>

                <div className="chips-container">
                  {popularInterests.map((interest) => (
                    <button
                      type="button"
                      key={interest}
                      className={`profile-chip ${
                        selectedInterests.includes(interest) ? "chip-active" : ""
                      }`}
                      onClick={() =>
                        toggleSelection(interest, selectedInterests, setSelectedInterests)
                      }
                    >
                      {interest} {selectedInterests.includes(interest) ? "✓" : "+"}
                    </button>
                  ))}
                </div>

                <div className="custom-input-group">
                  <input
                    type="text"
                    placeholder="Add specific interest (e.g., Micro-mobility)..."
                    value={customInterest}
                    onChange={(e) => setCustomInterest(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        addCustomItem(customInterest, selectedInterests, setSelectedInterests, setCustomInterest);
                      }
                    }}
                  />
                  <button
                    type="button"
                    className="add-chip-btn"
                    onClick={() =>
                      addCustomItem(customInterest, selectedInterests, setSelectedInterests, setCustomInterest)
                    }
                  >
                    Add
                  </button>
                </div>
              </div>

              {/* 3. Domain Knowledge */}
              <div className="profile-section-card">
                <div className="section-header">
                  <span className="section-number">3</span>
                  <div>
                    <h3>Domain Expertise & Industry Moats</h3>
                    <p>Which vertical do you understand better than others?</p>
                  </div>
                </div>

                <div className="chips-container">
                  {domainOptions.map((domain) => (
                    <button
                      type="button"
                      key={domain}
                      className={`profile-chip ${
                        selectedDomains.includes(domain) ? "chip-active" : ""
                      }`}
                      onClick={() =>
                        toggleSelection(domain, selectedDomains, setSelectedDomains)
                      }
                    >
                      {domain} {selectedDomains.includes(domain) ? "✓" : "+"}
                    </button>
                  ))}
                </div>

                <div className="custom-input-group">
                  <input
                    type="text"
                    placeholder="Add custom industry (e.g., Veterinary, Maritime)..."
                    value={customDomain}
                    onChange={(e) => setCustomDomain(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        addCustomItem(customDomain, selectedDomains, setSelectedDomains, setCustomDomain);
                      }
                    }}
                  />
                  <button
                    type="button"
                    className="add-chip-btn"
                    onClick={() =>
                      addCustomItem(customDomain, selectedDomains, setSelectedDomains, setCustomDomain)
                    }
                  >
                    Add
                  </button>
                </div>
              </div>

              {/* 4. Experience & Background */}
              <div className="profile-section-card">
                <div className="section-header">
                  <span className="section-number">4</span>
                  <div>
                    <h3>Professional Experience</h3>
                    <p>Tell us about your background and past roles.</p>
                  </div>
                </div>

                <div className="radio-group-vertical">
                  {[
                    "Student / Aspiring Founder",
                    "1 - 3 Years (Early Career)",
                    "3 - 5 Years (Mid-level)",
                    "6 - 10+ Years (Senior / Leadership)",
                  ].map((exp) => (
                    <label key={exp} className="radio-item-box">
                      <input
                        type="radio"
                        name="experienceLevel"
                        value={exp}
                        checked={experienceLevel === exp}
                        onChange={() => setExperienceLevel(exp)}
                      />
                      <span>{exp}</span>
                    </label>
                  ))}
                </div>

                <textarea
                  className="profile-textarea"
                  rows="3"
                  placeholder="Optional brief notes: e.g., 'Worked 4 years as a frontend engineer at a fintech startup, managed team of 3...'"
                  value={experienceSummary}
                  onChange={(e) => setExperienceSummary(e.target.value)}
                />
              </div>

              {/* 5. Budget */}
              <div className="profile-section-card">
                <div className="section-header">
                  <span className="section-number">5</span>
                  <div>
                    <h3>Starting Budget & Capital</h3>
                    <p>What financial resources can you allocate initially?</p>
                  </div>
                </div>

                <div className="radio-group-vertical">
                  {budgetOptions.map((opt) => (
                    <label key={opt} className="radio-item-box">
                      <input
                        type="radio"
                        name="budget"
                        value={opt}
                        checked={budget === opt}
                        onChange={() => setBudget(opt)}
                      />
                      <span>{opt}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* 6. Startup Goals */}
              <div className="profile-section-card">
                <div className="section-header">
                  <span className="section-number">6</span>
                  <div>
                    <h3>Founder Ambition & Goals</h3>
                    <p>What is your ultimate definition of startup success?</p>
                  </div>
                </div>

                <div className="radio-group-vertical">
                  {goalOptions.map((goal) => (
                    <label key={goal} className="radio-item-box">
                      <input
                        type="radio"
                        name="startupGoal"
                        value={goal}
                        checked={startupGoal === goal}
                        onChange={() => setStartupGoal(goal)}
                      />
                      <span>{goal}</span>
                    </label>
                  ))}
                </div>

                <input
                  type="text"
                  className="profile-text-input"
                  placeholder="Target audience preference (optional, e.g., remote workers, small clinics)..."
                  value={targetAudience}
                  onChange={(e) => setTargetAudience(e.target.value)}
                />
              </div>
            </div>

            {/* Bottom Action Footer */}
            <div className="profile-actions-bar">
              <div className="actions-info">
                <strong>🤖 Multi-Agent Recommendation Engine:</strong>
                <span>
                  LangGraph will cross-reference your {selectedSkills.length} skills & {selectedDomains.length} domains to discover actionable, high-probability ideas.
                </span>
              </div>

              <button
                type="submit"
                className="generate-ideas-btn"
                disabled={isGenerating}
              >
                {isGenerating ? (
                  <>
                    <span className="btn-spinner"></span> Synthesizing Concepts...
                  </>
                ) : (
                  <>🚀 Generate Startup Ideas →</>
                )}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}