import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  AlertTriangle,
  Bot,
  CheckCircle2,
  ChevronRight,
  Download,
  FileJson,
  FlaskConical,
  History,
  Play,
  RefreshCcw,
  ShieldCheck,
  Sparkles,
  TerminalSquare,
  Wand2,
  XCircle,
} from "lucide-react";
import { downloadReport, generateTests, runTests } from "./api/client";
import "./styles.css";

const statusIcon = {
  PASSED: CheckCircle2,
  FAILED: XCircle,
  HEALED: ShieldCheck,
  RUNNING: Activity,
  PENDING: TerminalSquare,
};

function App() {
  const [url, setUrl] = useState("https://example.com");
  const [feature, setFeature] = useState("login form validation");
  const [projectId, setProjectId] = useState("");
  const [testCases, setTestCases] = useState([]);
  const [report, setReport] = useState(null);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  const summary = useMemo(() => {
    if (!report) return { total: 0, passed: 0, failed: 0, healed: 0 };
    return {
      total: report.total_tests,
      passed: report.passed,
      failed: report.failed,
      healed: report.healed,
    };
  }, [report]);

  async function handleGenerate(event) {
    event.preventDefault();
    setBusy("generate");
    setError("");
    setReport(null);
    try {
      const data = await generateTests({ url, feature });
      setProjectId(data.project_id);
      setTestCases(data.test_cases);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setBusy("");
    }
  }

  async function handleRun() {
    if (!projectId) return;
    setBusy("run");
    setError("");
    try {
      const data = await runTests(projectId);
      setReport(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setBusy("");
    }
  }

  async function handleDownloadReport() {
    if (!projectId) return;
    setBusy("download");
    setError("");
    try {
      await downloadReport(projectId);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setBusy("");
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar" aria-label="Application navigation">
        <div className="brand">
          <div className="brand-mark"><Bot size={22} /></div>
          <div>
            <strong>AI QA Platform</strong>
            <span>Self-healing Selenium</span>
          </div>
        </div>
        <nav className="nav-list">
          <a href="#project"><FlaskConical size={18} /> Project</a>
          <a href="#suite"><FileJson size={18} /> Test Suite</a>
          <a href="#execution"><Activity size={18} /> Execution</a>
          <a href="#reports"><History size={18} /> Reports</a>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Automation control plane</p>
            <h1>AI QA Automation Web Platform</h1>
          </div>
          <div className="health-pill"><ShieldCheck size={16} /> Demo engine ready</div>
        </header>

        {error && (
          <div className="alert" role="alert">
            <AlertTriangle size={18} />
            <span>{error}</span>
          </div>
        )}

        <section className="grid two" id="project">
          <form className="panel input-panel" onSubmit={handleGenerate}>
            <div className="panel-heading">
              <Sparkles size={20} />
              <div>
                <h2>Project Input</h2>
                <p>Generate structured positive, negative, and edge tests.</p>
              </div>
            </div>
            <label>
              Website URL
              <input
                type="url"
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                onBlur={() => setUrl((value) => value.trim())}
                required
                placeholder="https://example.com"
                autoComplete="url"
              />
            </label>
            <label>
              Feature description
              <textarea
                value={feature}
                onChange={(event) => setFeature(event.target.value)}
                onBlur={() => setFeature((value) => value.trim())}
                required
                minLength={3}
                rows={5}
                placeholder="login, checkout, contact form validation"
              />
            </label>
            <button className="primary-action" type="submit" disabled={busy === "generate"}>
              {busy === "generate" ? <RefreshCcw size={18} className="spin" /> : <Wand2 size={18} />}
              Generate Test Suite
            </button>
          </form>

          <div className="panel architecture-panel">
            <div className="panel-heading">
              <TerminalSquare size={20} />
              <div>
                <h2>Execution Flow</h2>
                <p>AI generation to Selenium recovery in one pipeline.</p>
              </div>
            </div>
            {["Generate cases", "Run Selenium steps", "Detect locator failures", "Rank healed selectors", "Export report"].map((item) => (
              <div className="flow-row" key={item}>
                <span>{item}</span>
                <ChevronRight size={18} />
              </div>
            ))}
          </div>
        </section>

        <section className="panel" id="suite">
          <div className="section-title">
            <div>
              <h2>Test Suite</h2>
              <p>{testCases.length ? `${testCases.length} generated cases for ${feature}` : "Generate a suite to review Selenium-ready steps."}</p>
            </div>
            <button className="secondary-action" onClick={handleRun} disabled={!projectId || busy === "run"}>
              {busy === "run" ? <RefreshCcw size={18} className="spin" /> : <Play size={18} />}
              Run Tests
            </button>
          </div>
          <div className="case-grid">
            {testCases.map((testCase) => (
              <article className="case-card" key={testCase.id}>
                <div className="case-meta">
                  <span>{testCase.type}</span>
                  <span>{testCase.severity}</span>
                </div>
                <h3>{testCase.title}</h3>
                <ol>
                  {testCase.steps.map((step) => (
                    <li key={step.id}>
                      <code>{step.action}</code>
                      <span>{step.description}</span>
                    </li>
                  ))}
                </ol>
                <p className="expected">{testCase.expected_result}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="grid stats" id="execution">
          <Metric label="Total" value={summary.total} />
          <Metric label="Passed" value={summary.passed} tone="pass" />
          <Metric label="Failed" value={summary.failed} tone="fail" />
          <Metric label="Healed" value={summary.healed} tone="heal" />
        </section>

        <section className="panel" id="reports">
          <div className="section-title">
            <div>
              <h2>Execution Dashboard</h2>
              <p>Step logs show passed, failed, and self-healed actions.</p>
            </div>
            {report && (
              <button className="secondary-action" type="button" onClick={handleDownloadReport} disabled={busy === "download"}>
                {busy === "download" ? <RefreshCcw size={18} className="spin" /> : <Download size={18} />}
                Download JSON
              </button>
            )}
          </div>
          <div className="result-list">
            {(report?.results || []).map((result) => {
              const Icon = statusIcon[result.status] || TerminalSquare;
              return (
                <article className="result-card" key={result.test_id}>
                  <div className="result-header">
                    <Icon size={20} />
                    <h3>{result.title}</h3>
                    <span className={`status ${result.status.toLowerCase()}`}>{result.status}</span>
                  </div>
                  <div className="log-list">
                    {result.logs.map((log) => (
                      <div className="log-row" key={`${result.test_id}-${log.step_id}-${log.timestamp}`}>
                        <code>{log.status}</code>
                        <span>{log.message}</span>
                        {log.healed_selector && <strong>{log.healed_selector}</strong>}
                      </div>
                    ))}
                  </div>
                  {result.bug_report && (
                    <div className="bug-report">
                      <strong>{result.bug_report.title}</strong>
                      <span>{result.bug_report.actual}</span>
                    </div>
                  )}
                </article>
              );
            })}
            {!report && <p className="empty-state">Run tests to populate execution logs and reports.</p>}
          </div>
        </section>
      </section>
    </main>
  );
}

function Metric({ label, value, tone = "" }) {
  return (
    <div className={`metric ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
