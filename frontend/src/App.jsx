import { useEffect, useState } from "react";
import { classifyTicket, fetchStats, fetchTickets } from "./api";

const LABEL_NAMES = {
  billing: "Billing",
  technical_support: "Technical Support",
  account_access: "Account Access",
  shipping: "Shipping",
  general: "General",
};

function labelName(label) {
  return LABEL_NAMES[label] || label;
}

export default function App() {
  const [text, setText] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function refresh() {
    try {
      const [history, statsData] = await Promise.all([
        fetchTickets(20),
        fetchStats(),
      ]);
      setTickets(history);
      setStats(statsData);
    } catch {
      setError("Could not reach the API. Is the backend running on port 8000?");
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!text.trim()) return;
    setSubmitting(true);
    setError("");
    try {
      const result = await classifyTicket(text.trim());
      setPrediction(result);
      setText("");
      await refresh();
    } catch (err) {
      setError(err.message || "Classification failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page">
      <header>
        <h1>AI Ticket Classifier</h1>
        <p>
          Paste a customer support ticket and the model predicts its category:
          billing, technical support, account access, shipping, or general.
        </p>
      </header>

      <main>
        <section className="card">
          <h2>Classify a ticket</h2>
          <form onSubmit={handleSubmit}>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="e.g. I was charged twice for my subscription this month and need a refund."
              rows={4}
            />
            <button type="submit" disabled={submitting || !text.trim()}>
              {submitting ? "Classifying…" : "Classify"}
            </button>
          </form>
          {error && <p className="error">{error}</p>}
          {prediction && (
            <div className="prediction">
              <span className="prediction-label">{labelName(prediction.label)}</span>
              <span className="prediction-confidence">
                {(prediction.confidence * 100).toFixed(1)}% confidence
              </span>
              <div className="confidence-bar">
                <div
                  className="confidence-fill"
                  style={{ width: `${prediction.confidence * 100}%` }}
                />
              </div>
            </div>
          )}
        </section>

        <section className="card">
          <h2>Classifications by category</h2>
          {stats ? (
            <ul className="stats">
              {Object.entries(stats.counts).map(([label, count]) => (
                <li key={label}>
                  <span>{labelName(label)}</span>
                  <strong>{count}</strong>
                </li>
              ))}
              <li className="stats-total">
                <span>Total classified</span>
                <strong>{stats.total}</strong>
              </li>
            </ul>
          ) : (
            <p>No stats loaded yet.</p>
          )}
        </section>

        <section className="card wide">
          <h2>Recent classifications</h2>
          {tickets.length === 0 ? (
            <p>No tickets classified yet. Submit one above to get started.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Ticket</th>
                  <th>Predicted label</th>
                  <th>Confidence</th>
                  <th>When</th>
                </tr>
              </thead>
              <tbody>
                {tickets.map((ticket) => (
                  <tr key={ticket.id}>
                    <td>{ticket.text}</td>
                    <td>{labelName(ticket.label)}</td>
                    <td>{(ticket.confidence * 100).toFixed(1)}%</td>
                    <td>{new Date(ticket.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </main>
    </div>
  );
}
