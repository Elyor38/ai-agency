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

      const result = await runCompanyWorkflow(company.id);

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
          <p>{loading ? "..." : stats.companies}</p>
        </div>

        <div className="card">
          <h2>📊 Audits</h2>
          <p>{loading ? "..." : stats.audits}</p>
        </div>

        <div className="card">
          <h2>⭐ Scores</h2>
          <p>{loading ? "..." : stats.scores}</p>
        </div>

        <div className="card">
          <h2>✉️ Emails</h2>
          <p>{loading ? "..." : stats.writers}</p>
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
                  <td>{company.city || "—"}</td>
                  <td>{company.sector || "—"}</td>

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
    </div>
  );
}


export default App;