import Navbar from "../components/Navbar";
import UserSync from "../components/UserSync";

export default function Dashboard() {
  return (
    <div className="dashboard">
      <Navbar />
      <UserSync />

      <main className="dashboard-body">
        <div className="glass-card">
          <h3>Welcome 👋</h3>
          <p>Select a market and product to get started.</p>
        </div>
      </main>
    </div>
  );
}
