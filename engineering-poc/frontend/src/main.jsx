import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const API = "/api/tasks";

function App() {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(API).then((response) => response.json()).then((data) => setTasks(data.tasks));
  }, []);

  async function addTask(event) {
    event.preventDefault();
    setError("");
    const response = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    const data = await response.json();
    if (!response.ok) {
      setError(data.detail);
      return;
    }
    setTasks((current) => [...current, data.title]);
    setTitle("");
  }

  return (
    <main>
      <section className="card">
        <p className="eyebrow">ENGINEERING POC</p>
        <h1>Small tasks, clear progress.</h1>
        <p className="intro">A tiny full-stack app for testing an agentic coding loop.</p>
        <form onSubmit={addTask}>
          <label htmlFor="task-title">New task</label>
          <div className="form-row">
            <input id="task-title" value={title} onChange={(event) => setTitle(event.target.value)} placeholder="e.g. Review API contract" />
            <button type="submit">Add task</button>
          </div>
        </form>
        {error && <p role="alert" className="error">{error}</p>}
        <h2>Tasks</h2>
        {tasks.length ? <ul>{tasks.map((task, index) => <li key={`${task}-${index}`}>{task}</li>)}</ul> : <p className="empty">No tasks yet.</p>}
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<StrictMode><App /></StrictMode>);

