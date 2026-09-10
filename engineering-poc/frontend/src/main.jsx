import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const API = "/api/tasks";
const JOBS_API = "/api/jobs";

function App() {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");
  const [job, setJob] = useState(null);
  const [jobError, setJobError] = useState("");

  useEffect(() => {
    fetch(API).then((response) => response.json()).then((data) => setTasks(data.tasks));
  }, []);

  useEffect(() => {
    if (!job || !["queued", "running"].includes(job.status)) return undefined;
    const timer = setTimeout(async () => {
      try {
        const response = await fetch(`${JOBS_API}/${job.job_id}`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Could not retrieve job status");
        setJob(data);
      } catch (requestError) {
        setJobError(requestError.message);
      }
    }, 150);
    return () => clearTimeout(timer);
  }, [job]);

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

  async function submitHealthCheck() {
    setJobError("");
    try {
      const response = await fetch(JOBS_API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_type: "health-check" }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Could not submit job");
      setJob({ ...data, result: null, error: null });
    } catch (requestError) {
      setJobError(requestError.message);
    }
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
        <section className="job-panel" aria-labelledby="job-heading">
          <h2 id="job-heading">Backend job</h2>
          <p className="intro">Run a health check asynchronously.</p>
          <button type="button" onClick={submitHealthCheck}>Run health check</button>
          {job && <p className="job-status">Job status: <strong>{job.status}</strong></p>}
          {job?.status === "completed" && <pre aria-label="Job result">{JSON.stringify(job.result, null, 2)}</pre>}
          {job?.status === "failed" && <p role="alert" className="error">{job.error}</p>}
          {jobError && <p role="alert" className="error">{jobError}</p>}
        </section>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<StrictMode><App /></StrictMode>);
