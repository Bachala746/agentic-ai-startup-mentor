import { Routes, Route } from "react-router-dom";
import AgentInsights from "./pages/AgentInsights";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import SavedPlans from "./pages/SavedPlans";
import IdeaOverview from "./pages/IdeaOverview";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/home" element={<Home />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/saved-plans" element={<SavedPlans />} />
      <Route path="/agent-insights" element={<AgentInsights />} />
      <Route path="/idea-overview" element={<IdeaOverview />}/>
    </Routes>
  );
}

export default App;