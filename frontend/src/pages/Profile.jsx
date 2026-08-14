import { useNavigate } from "react-router-dom";

export default function Profile() {
  const navigate = useNavigate();

  return (
    <div>
      <h1>Profile Page</h1>

      <button onClick={() => navigate("/home")}>
        Back to Startup Mentor
      </button>
    </div>
  );
}