# Agentic AI Personalized Startup Mentor

An AI-powered startup mentoring platform that helps students and aspiring entrepreneurs analyze, validate, and develop their startup ideas through personalized AI guidance.

## Overview

The Agentic AI Personalized Startup Mentor analyzes the user's profile and startup idea to provide structured startup guidance. The system uses specialized AI agents for different aspects of startup analysis and combines their outputs to generate a personalized startup plan and roadmap.

## Key Features

- User Profile-based personalized guidance
- Startup Idea Analysis
- Market Analysis
- Financial Analysis
- Risk Analysis
- AI Mentor / Decision Support
- Web Search for relevant information
- Personalized Startup Plan
- Step-by-Step Startup Roadmap
- SQLite-based data persistence

## Workflow

User Profile + Startup Idea
        ↓
React Frontend
        ↓
FastAPI Backend
        ↓
LangChain / LangGraph
        ↓
Specialized AI Agents
        ↓
Web Search + Gemini
        ↓
Combined AI Insights
        ↓
Personalized Startup Plan
        ↓
Step-by-Step Roadmap
        ↓
SQLite Database

## Specialized AI Agents

### Market Analysis Agent
Analyzes market demand, trends, target customers, opportunities, and competitors.

### Financial Analysis Agent
Analyzes financial feasibility, costs, budget, pricing, and possible revenue models.

### Risk Analysis Agent
Identifies potential technical, operational, security, legal, and other startup-related risks.

### Decision / Mentor Agent
Combines the outputs from different agents and provides personalized recommendations.

## Technology Stack

- React.js
- Vite
- Tailwind CSS
- Python
- FastAPI
- Uvicorn
- Gemini API
- LangChain
- LangGraph
- SQLite
- Web Search
- Git & GitHub

## Project Structure

```text
Agentic-AI-Startup-Mentor/
│
├── backend/
│   ├── database.py
│   ├── main.py
│   ├── web_search.py
│   ├── startup_mentor.db
│   └── .env
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── docs/
├── README.md
└── run.txt