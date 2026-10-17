import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./ProfileIdeaGeneration.css";

const API_BASE_URL =
  (typeof process !== "undefined" && process.env?.REACT_APP_API_URL) ||
  "http://localhost:8000";

export default function ProfileIdeaGeneration() {
  const navigate = useNavigate();
  const location = useLocation();

  // Saved user profile loaded from startupUsers[currentUserEmail].profile
  const [savedProfile, setSavedProfile] = useState(null);
  const [currentUserEmail, setCurrentUserEmail] = useState("");

  // 1. Skills
  const [selectedSkills, setSelectedSkills] = useState(["Full-Stack Web Dev", "AI & LLMs"]);
  const [customSkill, setCustomSkill] = useState("");

  // 2. Interests
  const [selectedInterests, setSelectedInterests] = useState(["B2B Productivity", "Creator Economy"]);
  const [customInterest, setCustomInterest] = useState("");

  // 3. Experience
  const [experienceLevel, setExperienceLevel] = useState("3 - 5 Years (Mid-level)");
  const [experienceSummary, setExperienceSummary] = useState("");

  // 4. Budget (in Indian Rupees - ₹)
  const [budget, setBudget] = useState("₹50,000 - ₹5,00,000 (Bootstrapped)");

  // 5. Domain Knowledge
  const [selectedDomains, setSelectedDomains] = useState(["Software & SaaS", "E-Commerce"]);
  const [customDomain, setCustomDomain] = useState("");

  // 6. Startup Goals
  const [startupGoal, setStartupGoal] = useState("Profitable Cash-Flow Micro-SaaS");
  const [targetAudience, setTargetAudience] = useState("");

  // AI Generation States
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState(null);
  const [generatedIdeas, setGeneratedIdeas] = useState([]);
  const [selectedIdeaName, setSelectedIdeaName] = useState("");

  // Load profile from localStorage: startupUsers[currentUserEmail].profile
  useEffect(() => {
    try {
      const email = localStorage.getItem("currentUserEmail");
      setCurrentUserEmail(email || "");

      const startupUsersRaw = localStorage.getItem("startupUsers");
      if (email && startupUsersRaw) {
        const startupUsers = JSON.parse(startupUsersRaw);
        const userRecord = startupUsers?.[email];
        const profileData = userRecord?.profile;

        if (profileData) {
          setSavedProfile({
            fullName: profileData.fullName || userRecord.fullName || "",
            skills: profileData.skills || [],
            interests: profileData.interests || [],
            experience: profileData.experience || "",
            budget: profileData.budget || "",
            goals: profileData.goals || "",
          });
          return;
        }
      }
      setSavedProfile(null);
    } catch (error) {
      console.error("Error reading startupUsers profile from localStorage:", error);
      setSavedProfile(null);
    }
  }, []);

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

  // Budget Options in Indian Rupees (₹)
  const budgetOptions = [
    "₹0 - ₹50,000 (Shoestring / Zero-Capital)",
    "₹50,000 - ₹5,00,000 (Bootstrapped)",
    "₹5,00,000 - ₹25,00,000 (Angel / Self-Funded)",
    "₹25,00,000+ (Seeking VC / High-Capital)",
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

  const parseList = (val) => {
    if (!val) return [];
    if (Array.isArray(val)) return val;
    if (typeof val === "string") {
      return val
        .split(/[,|\n]/)
        .map((s) => s.trim())
        .filter(Boolean);
    }
    return [];
  };

  // Helper to ensure cost string is cleanly displayed in Indian Rupees (₹)
  const formatCostINR = (costStr) => {
    if (!costStr) return "₹50,000 - ₹1,50,000";
    let cleaned = String(costStr).replace(/\$/g, "₹").trim();
    if (!cleaned.includes("₹") && !cleaned.toLowerCase().includes("rs")) {
      cleaned = `₹${cleaned}`;
    }
    return cleaned;
  };

  // Generate 5 Personalized Startup Ideas via backend Gemini endpoint
  const handleGenerateIdeas = async (e) => {
    if (e) e.preventDefault();
    setIsGenerating(true);
    setGenerationError(null);

    const formResponses = {
      skills: selectedSkills,
      interests: selectedInterests,
      experienceLevel,
      experienceSummary: experienceSummary.trim(),
      budget,
      domainKnowledge: selectedDomains,
      startupGoal,
      targetAudience: targetAudience.trim(),
    };

    // Save profile to local storage for downstream workflows
    localStorage.setItem("founderProfile", JSON.stringify(formResponses));

    try {
      const response = await fetch(`${API_BASE_URL}/generate-profile-ideas`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          savedProfile: savedProfile || {},
          formResponses: formResponses,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const message =
          errorData?.detail?.message ||
          (typeof errorData?.detail === "string" ? errorData.detail : null) ||
          "Failed to generate startup ideas. Please try again.";
        throw new Error(message);
      }

      const data = await response.json();
      const ideas = data?.ideas || [];

      if (!ideas || ideas.length === 0) {
        throw new Error("No ideas were returned by the AI service. Please retry.");
      }

      setGeneratedIdeas(ideas);

      // Smooth scroll to results
      setTimeout(() => {
        const el = document.getElementById("generated-ideas-results");
        if (el) {
          el.scrollIntoView({ behavior: "smooth" });
        }
      }, 100);
    } catch (err) {
      console.error("Idea generation error:", err);
      setGenerationError(err.message || "An unexpected error occurred while generating ideas.");
    } finally {
      setIsGenerating(false);
    }
  };

  // Select an idea and transition into existing /idea-overview workflow
  const handleSelectIdea = (idea) => {
    setSelectedIdeaName(idea.name);

    const ideaTitleAndDesc = `${idea.name}: ${idea.shortDescription}`;

    // Store selected idea and match explanation into localStorage
    localStorage.setItem("startupIdea", ideaTitleAndDesc);
    localStorage.setItem("currentStartupIdea", ideaTitleAndDesc);
    localStorage.setItem("selectedStartupIdea", JSON.stringify(idea));
    localStorage.setItem("selectedIdea", JSON.stringify(idea));
    localStorage.setItem("profileMatchExplanation", idea.matchExplanation || "");
    localStorage.setItem("selectedIdeaExplanation", idea.matchExplanation || "");

    // Navigate to the existing idea-overview route, providing the idea payload
    navigate("/idea-overview", {
      state: {
        startupIdea: ideaTitleAndDesc,
        ideaTitle: idea.name,
        ideaDescription: idea.shortDescription,
        selectedIdea: idea,
        matchExplanation: idea.matchExplanation,
      },
    });
  };

  const savedSkillsList = parseList(savedProfile?.skills);
  const savedInterestsList = parseList(savedProfile?.interests);

  const hasAnySavedData = Boolean(
    savedProfile &&
      (savedProfile.fullName ||
        savedSkillsList.length > 0 ||
        savedInterestsList.length > 0 ||
        savedProfile.experience ||
        savedProfile.budget ||
        savedProfile.goals)
  );

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

        {/* Content Area with Form & Saved Profile Card Side-by-Side */}
        <div className="workspace-content">
          <div className="discovery-split-layout">
            {/* Form */}
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
                          addCustomItem(
                            customInterest,
                            selectedInterests,
                            setSelectedInterests,
                            setCustomInterest
                          );
                        }
                      }}
                    />
                    <button
                      type="button"
                      className="add-chip-btn"
                      onClick={() =>
                        addCustomItem(
                          customInterest,
                          selectedInterests,
                          setSelectedInterests,
                          setCustomInterest
                        )
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
                          addCustomItem(
                            customDomain,
                            selectedDomains,
                            setSelectedDomains,
                            setCustomDomain
                          );
                        }
                      }}
                    />
                    <button
                      type="button"
                      className="add-chip-btn"
                      onClick={() =>
                        addCustomItem(
                          customDomain,
                          selectedDomains,
                          setSelectedDomains,
                          setCustomDomain
                        )
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

                {/* 5. Budget (in Indian Rupees - ₹) */}
                <div className="profile-section-card">
                  <div className="section-header">
                    <span className="section-number">5</span>
                    <div>
                      <h3>Starting Budget & Capital (INR - ₹)</h3>
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
                    Gemini analyzes your saved profile and discovery preferences using a 5-pillar compatibility model to generate 5 tailored startup ventures in Indian Rupees (₹).
                  </span>
                </div>

                <button
                  type="submit"
                  className="generate-ideas-btn"
                  disabled={isGenerating}
                >
                  {isGenerating ? (
                    <>
                      <span className="btn-spinner"></span> Synthesizing 5 Concepts...
                    </>
                  ) : (
                    <>🚀 Generate Startup Ideas →</>
                  )}
                </button>
              </div>
            </form>

            {/* Saved Founder Profile Card */}
            <aside className="saved-profile-sidebar-card">
              <div className="saved-profile-header">
                <div className="saved-profile-title-area">
                  <span className="saved-profile-badge-icon">👤</span>
                  <div>
                    <h3>Saved Founder Profile</h3>
                    <p>Loaded from startupUsers</p>
                  </div>
                </div>
                <button
                  type="button"
                  className="edit-profile-link-btn"
                  onClick={() => navigate("/profile")}
                  title="Edit details in User Profile"
                >
                  Edit ⚙️
                </button>
              </div>

              {hasAnySavedData ? (
                <div className="saved-profile-content">
                  {/* fullName */}
                  <div className="saved-profile-identity">
                    <div className="founder-avatar-circle">
                      {savedProfile.fullName ? savedProfile.fullName.charAt(0).toUpperCase() : "👤"}
                    </div>
                    <div className="founder-identity-text">
                      <div className="founder-name">
                        {savedProfile.fullName || "Unnamed Founder"}
                      </div>
                      {currentUserEmail && <div className="founder-email">{currentUserEmail}</div>}
                    </div>
                  </div>

                  {/* skills */}
                  <div className="saved-profile-item">
                    <span className="saved-item-label">Skills</span>
                    {savedSkillsList.length > 0 ? (
                      <div className="saved-tags-wrap">
                        {savedSkillsList.map((skill, idx) => (
                          <span key={idx} className="saved-tag-pill skill-pill">
                            {skill}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="saved-empty-hint">Not specified</span>
                    )}
                  </div>

                  {/* interests */}
                  <div className="saved-profile-item">
                    <span className="saved-item-label">Interests</span>
                    {savedInterestsList.length > 0 ? (
                      <div className="saved-tags-wrap">
                        {savedInterestsList.map((interest, idx) => (
                          <span key={idx} className="saved-tag-pill interest-pill">
                            {interest}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="saved-empty-hint">Not specified</span>
                    )}
                  </div>

                  {/* experience */}
                  <div className="saved-profile-item">
                    <span className="saved-item-label">Experience</span>
                    {savedProfile.experience ? (
                      <p className="saved-item-text">{savedProfile.experience}</p>
                    ) : (
                      <span className="saved-empty-hint">Not specified</span>
                    )}
                  </div>

                  {/* budget */}
                  <div className="saved-profile-item">
                    <span className="saved-item-label">Budget</span>
                    {savedProfile.budget ? (
                      <p className="saved-item-text">{formatCostINR(savedProfile.budget)}</p>
                    ) : (
                      <span className="saved-empty-hint">Not specified</span>
                    )}
                  </div>

                  {/* goals */}
                  <div className="saved-profile-item">
                    <span className="saved-item-label">Goals</span>
                    {savedProfile.goals ? (
                      <p className="saved-item-text">
                        {Array.isArray(savedProfile.goals)
                          ? savedProfile.goals.join(", ")
                          : savedProfile.goals}
                      </p>
                    ) : (
                      <span className="saved-empty-hint">Not specified</span>
                    )}
                  </div>

                  <div className="saved-profile-sync-note">
                    <span className="sync-dot"></span>
                    Both saved profile traits & form choices guide your idea generation.
                  </div>
                </div>
              ) : (
                <div className="saved-profile-empty">
                  <div className="empty-icon">📋</div>
                  <h4>No Saved Profile Found</h4>
                  <p>
                    No profile was found in <code>startupUsers</code>. Complete your details on the User Profile page to tailor your ideas.
                  </p>
                  <button
                    type="button"
                    className="complete-profile-btn"
                    onClick={() => navigate("/profile")}
                  >
                    Complete User Profile →
                  </button>
                </div>
              )}
            </aside>
          </div>

          {/* Loading Indicator State */}
          {isGenerating && (
            <div className="generation-loading-container">
              <div className="loading-orbit-spinner">
                <div className="orbit-core"></div>
              </div>
              <h3>Synthesizing 5 Startup Concepts</h3>
              <p>
                Our AI is cross-referencing your profile, superpowers, capital budget in Indian Rupees (₹), and domain background
                to formulate high-probability opportunities...
              </p>
            </div>
          )}

          {/* Error and Retry State */}
          {generationError && !isGenerating && (
            <div className="generation-error-container">
              <div className="error-icon">⚠️</div>
              <div className="error-content">
                <h4>Unable to Generate Startup Ideas</h4>
                <p>{generationError}</p>
              </div>
              <button
                type="button"
                className="retry-btn"
                onClick={handleGenerateIdeas}
              >
                🔄 Retry Generation
              </button>
            </div>
          )}

          {/* Generated 5 Ideas Section */}
          {generatedIdeas.length > 0 && !isGenerating && (
            <section id="generated-ideas-results" className="generated-ideas-section">
              <div className="ideas-section-header">
                <div>
                  <span className="ideas-badge">✨ AI Recommendations</span>
                  <h2>Personalized Startup Opportunities (5 Concepts)</h2>
                  <p className="scoring-disclaimer">
                    ℹ️ Profile match ratings (0–100%) are estimated compatibility scores evaluated across your skills, domain background, budget in INR (₹), and goals. They reflect structural fit, not commercial guarantees.
                  </p>
                </div>
                <button
                  type="button"
                  className="regenerate-secondary-btn"
                  onClick={handleGenerateIdeas}
                >
                  🔄 Regenerate
                </button>
              </div>

              <div className="ideas-grid">
                {generatedIdeas.map((idea, index) => {
                  const isSelected = selectedIdeaName === idea.name;
                  const match = idea.matchPercentage || 85;

                  return (
                    <article
                      key={index}
                      className={`startup-idea-card ${isSelected ? "selected-card" : ""}`}
                    >
                      {/* Card Header: Concept # and Prominent Match Badge */}
                      <div className="idea-card-header">
                        <span className="idea-index-pill">Concept #{index + 1}</span>
                        <div className="idea-match-score">
                          <span className="match-num">{match}%</span>
                          <span className="match-label">Match</span>
                        </div>
                      </div>

                      {/* Idea Title & Description */}
                      <div className="idea-heading-block">
                        <h3 className="idea-title">{idea.name}</h3>
                        <p className="idea-short-desc">{idea.shortDescription}</p>
                      </div>

                      {/* Problem & Solution */}
                      <div className="idea-ps-container">
                        <div className="ps-card ps-problem">
                          <span className="ps-tag tag-problem">Problem</span>
                          <p className="ps-text">{idea.problem}</p>
                        </div>
                        <div className="ps-card ps-solution">
                          <span className="ps-tag tag-solution">Solution</span>
                          <p className="ps-text">{idea.solution}</p>
                        </div>
                      </div>

                      {/* Highlighted "Why This Matches You" Section */}
                      <div className="idea-match-highlight">
                        <div className="match-highlight-header">
                          <span className="highlight-icon">🎯</span>
                          <h4>Why This Matches You</h4>
                        </div>
                        <p className="match-highlight-text">{idea.matchExplanation}</p>
                      </div>

                      {/* Key Details & Metrics Grid */}
                      <div className="idea-details-grid">
                        <div className="detail-item full-width-item">
                          <span className="detail-key">USP / Differentiator:</span>
                          <span className="detail-val">{idea.usp}</span>
                        </div>
                        <div className="detail-row-split">
                          <div className="detail-item">
                            <span className="detail-key">Difficulty:</span>
                            <span className={`difficulty-badge diff-${idea.difficulty?.toLowerCase()}`}>
                              {idea.difficulty || "Moderate"}
                            </span>
                          </div>
                          <div className="detail-item">
                            <span className="detail-key">Est. Launch Cost:</span>
                            <span className="detail-val cost-val">{formatCostINR(idea.estimatedCost)}</span>
                          </div>
                        </div>
                      </div>

                      {/* Select This Idea Button */}
                      <div className="card-action-footer">
                        <button
                          type="button"
                          className="select-idea-btn"
                          onClick={() => handleSelectIdea(idea)}
                        >
                          Select This Idea & Explore Overview →
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}