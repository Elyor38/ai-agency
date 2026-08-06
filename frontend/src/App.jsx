import { useEffect, useState } from "react";
import "./App.css";

import { getCompanies } from "./api/companyApi";
import { getDashboardStats } from "./api/dashboardApi";
import { getCompanyDetails } from "./api/companyDetailsApi";
import { runCompanyWorkflow } from "./api/workflowApi";
import CompanyDetails from "./components/CompanyDetails";


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
  const [selectedCompanyId, setSelectedCompanyId] = useState(null);
  const [companyDetails, setCompanyDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

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


  async function handleSelectCompany(companyId) {
    try {
      setSelectedCompanyId(companyId);
      setDetailsLoading(true);
      setError("");
      setSuccessMessage("");

      const details = await getCompanyDetails(companyId);

      setCompanyDetails(details);
    } catch (requestError) {
      console.error(requestError);

      setCompanyDetails(null);
      setError(requestError.message);
    } finally {
      setDetailsLoading(false);
    }
  }


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

      if (selectedCompanyId === company.id) {
        const refreshedDetails = await getCompanyDetails(
          company.id
        );

        setCompanyDetails(refreshedDetails);
      }
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

      <div className="dashboard-layout">
        <section className="companies-panel">
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
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {companies.map((company) => {
                  const isRunning =
                    runningCompanyId === company.id;

                  const isSelected =
                    selectedCompanyId === company.id;

                  return (
                    <tr
                      key={company.id}
                      className={
                        isSelected
                          ? "selected-row"
                          : ""
                      }
                    >
                      <td>
                        <button
                          type="button"
                          className="company-name-button"
                          onClick={() =>
                            handleSelectCompany(
                              company.id
                            )
                          }
                        >
                          {company.name}
                        </button>
                      </td>

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
                        <div className="table-actions">
                          <button
                            type="button"
                            className="details-button"
                            onClick={() =>
                              handleSelectCompany(
                                company.id
                              )
                            }
                          >
                            Voir la fiche
                          </button>

                          <button
                            type="button"
                            className="workflow-button"
                            disabled={
                              isRunning
                              || !company.website
                            }
                            onClick={() =>
                              handleRunWorkflow(company)
                            }
                          >
                            {isRunning
                              ? "Workflow en cours..."
                              : "Lancer le workflow"}
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </section>

        <aside className="details-panel">
          {detailsLoading ? (
            <p>Chargement de la fiche...</p>
          ) : companyDetails ? (
            <>
              <button
                type="button"
                className="close-details-button"
                onClick={() => {
                  setSelectedCompanyId(null);
                  setCompanyDetails(null);
                }}
              >
                Fermer la fiche
              </button>

              <CompanyDetails
                details={companyDetails}
              />
            </>
          ) : (
            <div className="empty-details">
              <h2>Fiche entreprise</h2>

              <p>
                Clique sur le nom d'une entreprise
                ou sur « Voir la fiche ».
              </p>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}


export default App;