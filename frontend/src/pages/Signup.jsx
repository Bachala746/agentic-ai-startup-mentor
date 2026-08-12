import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Signup.css';

export default function Signup() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [passwordStrength, setPasswordStrength] = useState({ score: 0, label: '' });

  const validateEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const evaluatePassword = (pass) => {
    setPassword(pass);
    if (!pass) {
      setPasswordStrength({ score: 0, label: '' });
      return;
    }
    let score = 0;
    if (pass.length >= 8) score++;
    if (/[A-Z]/.test(pass)) score++;
    if (/[0-9]/.test(pass)) score++;
    if (/[^A-Za-z0-9]/.test(pass)) score++;

    let label = 'Weak';
    if (score === 2) label = 'Fair';
    if (score === 3) label = 'Good';
    if (score >= 4) label = 'Strong';

    setPasswordStrength({ score, label });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!fullName.trim()) {
      setError('Please enter your full name.');
      return;
    }

    if (!validateEmail(email)) {
      setError('Please enter a valid email address.');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (!acceptTerms) {
      setError('You must accept the Terms & Conditions.');
      return;
    }

    setIsLoading(true);

    // Simulate backend account creation request
    setTimeout(() => {
      setIsLoading(false);
      navigate("/login");
    }, 1500);
  };

  return (
    <div className="signup-page-wrapper">
      {/* Floating Particle Background */}
      <div className="particles-container">
        {[...Array(15)].map((_, i) => (
          <div key={i} className={`particle particle-${i + 1}`}></div>
        ))}
      </div>

      {/* Background Glow Effects */}
      <div className="signup-glow-1"></div>
      <div className="signup-glow-2"></div>

      {/* Top Navigation: Back to Home */}
      <div className="signup-top-nav">
        <a href="#home" className="back-home-btn">
          <span>←</span> Back to Home
        </a>
      </div>

      <div className="signup-container">
        <div className="signup-wrapper">
          
          {/* Left Side: AI Illustration & Branding */}
          <div className="signup-left">
            <div className="logo-container">
              <span className="logo-icon">🚀</span>
              <span className="logo-text">Agentic AI Startup Mentor</span>
            </div>

            {/* Modern CSS AI Robot Illustration */}
            <div className="ai-robot-container">
              <div className="robot-head">
                <div className="robot-antenna">
                  <div className="antenna-ball"></div>
                </div>
                <div className="robot-ears left"></div>
                <div className="robot-ears right"></div>
                <div className="robot-face">
                  <div className="robot-eye left-eye">
                    <div className="pupil"></div>
                  </div>
                  <div className="robot-eye right-eye">
                    <div className="pupil"></div>
                  </div>
                  <div className="robot-smile"></div>
                </div>
              </div>
              <div className="robot-collar"></div>
              <div className="floating-badge badge-top">⚡ AI-Powered Innovation</div>
              <div className="floating-badge badge-bottom">🎯 Automated Validation</div>
            </div>

            <div className="left-content">
              <h1>Build the Future with AI</h1>
              <p>Join visionary entrepreneurs leveraging autonomous agent networks to design, validate, and scale breakout startups.</p>
              
              <div className="perks-list">
                <div className="perk-item">✓ Instant Business Plan Generation</div>
                <div className="perk-item">✓ 24/7 Autonomous AI Co-Founder</div>
                <div className="perk-item">✓ Verified Investor Matching</div>
              </div>
            </div>
          </div>

          {/* Right Side: Glass Signup Card */}
          <div className="signup-right">
            <div className="glass-card">
              <div className="card-header">
                <h2>Create Account</h2>
                <p>Start your autonomous startup journey today</p>
              </div>

              <button className="google-btn" type="button">
                <svg className="google-icon" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                </svg>
                Sign up with Google
              </button>

              <div className="divider">
                <span>or register with email</span>
              </div>

              {error && <div className="error-banner">{error}</div>}

              <form onSubmit={handleSubmit} className="signup-form">
                <div className="input-group">
                  <label htmlFor="fullName">Full Name</label>
                  <input
                    type="text"
                    id="fullName"
                    placeholder="Elon Musk"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required
                  />
                </div>

                <div className="input-group">
                  <label htmlFor="email">Email Address</label>
                  <input
                    type="email"
                    id="email"
                    placeholder="founder@startup.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>

                <div className="input-group">
                  <label htmlFor="password">Password</label>
                  <div className="password-wrapper">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      id="password"
                      placeholder="At least 8 characters"
                      value={password}
                      onChange={(e) => evaluatePassword(e.target.value)}
                      required
                    />
                    <button
                      type="button"
                      className="toggle-password"
                      onClick={() => setShowPassword(!showPassword)}
                      aria-label="Toggle password visibility"
                    >
                      {showPassword ? '👁️' : '👁️‍🗨️'}
                    </button>
                  </div>
                  {password && (
                    <div className="password-strength-container">
                      <div className="strength-bars">
                        <div className={`strength-bar ${passwordStrength.score >= 1 ? 'active-' + passwordStrength.label.toLowerCase() : ''}`}></div>
                        <div className={`strength-bar ${passwordStrength.score >= 2 ? 'active-' + passwordStrength.label.toLowerCase() : ''}`}></div>
                        <div className={`strength-bar ${passwordStrength.score >= 3 ? 'active-' + passwordStrength.label.toLowerCase() : ''}`}></div>
                        <div className={`strength-bar ${passwordStrength.score >= 4 ? 'active-' + passwordStrength.label.toLowerCase() : ''}`}></div>
                      </div>
                      <span className={`strength-text ${passwordStrength.label.toLowerCase()}`}>
                        {passwordStrength.label}
                      </span>
                    </div>
                  )}
                </div>

                <div className="input-group">
                  <label htmlFor="confirmPassword">Confirm Password</label>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="confirmPassword"
                    placeholder="Re-enter password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                  />
                </div>

                <div className="form-options">
                  <label className="custom-checkbox-label">
                    <input
                      type="checkbox"
                      checked={acceptTerms}
                      onChange={(e) => setAcceptTerms(e.target.checked)}
                    />
                    <span className="checkmark"></span>
                    <span>I accept the <a href="#terms" className="terms-link">Terms & Conditions</a></span>
                  </label>
                </div>

                <button type="submit" className="signup-submit-btn" disabled={isLoading}>
                  {isLoading ? (
                    <div className="spinner-container">
                      <div className="spinner"></div>
                      <span>Creating Account...</span>
                    </div>
                  ) : (
                    'Create Account 🚀'
                  )}
                </button>
              </form>

              <div className="card-footer-action">
                <p>Already have an account? <a href="#login" className="signin-link">Sign In</a></p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}