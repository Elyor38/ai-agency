import { useEffect, useState } from "react";
import "./App.css";

import { getCompanies } from "./api/companyApi";
import { getDashboardStats } from "./api/dashboardApi";
import { runCompanyWorkflow } from "./api/workflowApi";


function App() {
  const [companies, setCompanies] = useState([]);

  const [stats, setStats] = useState({
    companies: 0,
    audits: 0,
    scores: 0,
    writers: 0,
  });

  const [loading, setLoading] = useState(true);
  const [runningCompanyId, setRunningCompanyId] = useState(null);

  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const [workflowResult, setWorkflowResult] = useState(null);


  async function refreshDashboard() {
    const [companiesData, statsData] = await Promise.all([
      getCompanies(),
      getDashboardStats(),
    ]);

    setCompanies(companiesData);
    setStats(statsData);
  }


  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");

        await refreshDashboard();
      } catch (requestError) {
        console.error(requestError);

        setError(
          "Impossible de charger les données du dashboard."
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);


  async function handleRunWorkflow(company) {
    try {
      setRunningCompanyId(company.id);
      setError("");
      setSuccessMessage("");
      setWorkflowResult(null);

      const result = await runCompanyWorkflow(company.id);

      setWorkflowResult(result);

      setSuccessMessage(
        `Workflow terminé pour ${result.company_name}.`
      );

      await refreshDashboard();
    } catch (requestError) {
      console.error(requestError);

      setError(requestError.message);
    } finally {
      setRunningCompanyId(null);
    }
  }


  return (
    <div className="app">
      <header className="header">
        <h1>🚀 AI Agency</h1>

        <p>Assistant commercial intelligent</p>
      </header>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="success-message">
          {successMessage}
        </div>
      )}

      <div className="cards">
        <div className="card">
          <h2>🏢 Entreprises</h2>

          <p>
            {loading ? "..." : stats.companies}
          </p>
        </div>

        <div className="card">
          <h2>📊 Audits</h2>

          <p>
            {loading ? "..." : stats.audits}
          </p>
        </div>

        <div className="card">
          <h2>⭐ Scores</h2>

          <p>
            {loading ? "..." : stats.scores}
          </p>
        </div>

        <div className="card">
          <h2>✉️ Emails</h2>

          <p>
            {loading ? "..." : stats.writers}
          </p>
        </div>
      </div>

      <h2 className="section-title">
        Entreprises
      </h2>

      {loading ? (
        <p>Chargement...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Nom</th>
              <th>Ville</th>
              <th>Secteur</th>
              <th>Site</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            {companies.map((company) => {
              const isRunning =
                runningCompanyId === company.id;

              return (
                <tr key={company.id}>
                  <td>{company.name}</td>

                  <td>
                    {company.city || "—"}
                  </td>

                  <td>
                    {company.sector || "—"}
                  </td>

                  <td>
                    {company.website ? (
                      <a
                        href={company.website}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Voir le site
                      </a>
                    ) : (
                      "—"
                    )}
                  </td>

                  <td>
                    <button
                      type="button"
                      className="workflow-button"
                      disabled={
                        isRunning || !company.website
                      }
                      onClick={() =>
                        handleRunWorkflow(company)
                      }
                    >
                      {isRunning
                        ? "Workflow en cours..."
                        : "Lancer le workflow"}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      {workflowResult && (
        <section className="workflow-result">
          <div className="workflow-result-header">
            <div>
              <p className="eyebrow">
                Dernier workflow
              </p>

              <h2>
                {workflowResult.company_name}
              </h2>
            </div>

            <button
              type="button"
              className="close-button"
              onClick={() =>
                setWorkflowResult(null)
              }
            >
              Fermer
            </button>
          </div>

          <div className="result-grid">
            <article className="result-card">
              <h3>Audit</h3>

              <p>
                Score technique :
                <strong>
                  {" "}
                  {
                    workflowResult.audit
                      .technical_score
                  }
                  /100
                </strong>
              </p>

              <p>
                Code HTTP :
                <strong>
                  {" "}
                  {
                    workflowResult.audit
                      .http_status ?? "inconnu"
                  }
                </strong>
              </p>

              <p>
                Temps de réponse :
                <strong>
                  {" "}
                  {
                    workflowResult.audit
                      .response_time_ms ?? "—"
                  }
                  {" ms"}
                </strong>
              </p>

              <div className="result-text">
                {
                  workflowResult.audit
                    .ai_analysis
                }
              </div>
            </article>

            <article className="result-card">
              <h3>Score IA</h3>

              <div className="score-value">
                {
                  workflowResult.score
                    .global_score
                }
                /100
              </div>

              <p>
                Priorité :
                <strong>
                  {" "}
                  {
                    workflowResult.score
                      .priority
                  }
                </strong>
              </p>

              <h4>Forces</h4>

              <ul>
                {
                  workflowResult.score
                    .strengths
                    .map((item, index) => (
                      <li key={`${item}-${index}`}>
                        {item}
                      </li>
                    ))
                }
              </ul>

              <h4>Faiblesses</h4>

              <ul>
                {
                  workflowResult.score
                    .weaknesses
                    .map((item, index) => (
                      <li key={`${item}-${index}`}>
                        {item}
                      </li>
                    ))
                }
              </ul>

              <h4>Opportunités</h4>

              <ul>
                {
                  workflowResult.score
                    .opportunities
                    .map((item, index) => (
                      <li key={`${item}-${index}`}>
                        {item}
                      </li>
                    ))
                }
              </ul>

              <h4>Offre recommandée</h4>

              <p>
                {
                  workflowResult.score
                    .recommended_offer
                }
              </p>

              <h4>Résumé</h4>

              <p>
                {
                  workflowResult.score
                    .summary
                }
              </p>
            </article>

            <article className="result-card">
              <h3>Email commercial</h3>

              <p className="email-subject">
                {
                  workflowResult.writer
                    .email_subject
                }
              </p>

              <pre className="email-body">
                {
                  workflowResult.writer
                    .email_body
                }
              </pre>

              <h4>Proposition commerciale</h4>

              <p>
                {
                  workflowResult.writer
                    .commercial_offer
                }
              </p>

              <h4>Appel à l'action</h4>

              <p>
                {
                  workflowResult.writer
                    .call_to_action
                }
              </p>
            </article>
          </div>
        </section>
      )}
    </div>
  );
}


export default App;