import { useNavigate } from "react-router-dom";
import React, { useState } from 'react';
import './Login.css';

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const validateEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!validateEmail(email)) {
      setError('Please enter a valid email address.');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    setIsLoading(true);

    // Simulate backend authentication request
    setTimeout(() => {
      setIsLoading(false);
      navigate("/dashboard");
    }, 1500);
  };

  return (
    <div className="login-page-wrapper">
      {/* Floating Particle Background */}
      <div className="particles-container">
        {[...Array(15)].map((_, i) => (
          <div key={i} className={`particle particle-${i + 1}`}></div>
        ))}
      </div>

      {/* Background Glow Effects */}
      <div className="login-glow-1"></div>
      <div className="login-glow-2"></div>

      {/* Top Navigation: Back to Home */}
      <div className="login-top-nav">
        <a href="#home" className="back-home-btn">
          <span>←</span> Back to Home
        </a>
      </div>

      <div className="login-container">
        <div className="login-wrapper">
          
          {/* Left Side: AI Illustration & Quote */}
          <div className="login-left">
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
              <div className="floating-badge badge-top">⚡ Autonomous Neural Net</div>
              <div className="floating-badge badge-bottom">💡 24/7 Co-Founder AI</div>
            </div>

            <div className="left-content">
              <h1>Welcome Back!</h1>
              <p>Continue building your startup journey with advanced AI mentorship, deep validation, and intelligent agent workflows.</p>
              
              {/* AI Quote of the Day */}
              <div className="ai-quote-card">
                <span className="quote-icon">✨</span>
                <div className="quote-text-wrap">
                  <p className="quote-title">AI Quote of the Day</p>
                  <p className="quote-body">"The best way to predict the future of your startup is to build it with autonomous intelligence."</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side: Glass Login Card */}
          <div className="login-right">
            <div className="glass-card">
              <div className="card-header">
                <h2>Sign In</h2>
                <p>Enter your credentials to access your control panel</p>
              </div>

              <button className="google-btn" type="button">
                <svg className="google-icon" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                </svg>
                Continue with Google
              </button>

              <div className="divider">
                <span>or continue with email</span>
              </div>

              {error && <div className="error-banner">{error}</div>}

              <form onSubmit={handleSubmit} className="login-form">
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
                      placeholder="••••••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
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
                </div>

                <div className="form-options">
                  <label className="custom-checkbox-label">
                    <input
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                    />
                    <span className="checkmark"></span>
                    <span>Remember me</span>
                  </label>
                  <a href="#forgot" className="forgot-password">Forgot password?</a>
                </div>

                <button type="submit" className="login-submit-btn" disabled={isLoading}>
                  {isLoading ? (
                    <div className="spinner-container">
                      <div className="spinner"></div>
                      <span>Signing In...</span>
                    </div>
                  ) : (
                    'Sign In 🚀'
                  )}
                </button>
              </form>

              <div className="card-footer-action">
                <p>Don't have an account yet?</p>
                    <button
                      type="button"
                      className="btn-secondary-action"
                      onClick={() => navigate("/signup")}
                    >
                      Create New Account
                    </button>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}