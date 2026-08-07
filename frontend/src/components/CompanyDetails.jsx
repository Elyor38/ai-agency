import EmailCard from "./EmailCard";
import HistoryList from "./HistoryList";


const API_URL = "http://127.0.0.1:8000";


function CompanyDetails({ details }) {
  if (!details) {
    return null;
  }

  const company = details.company;
  const latestScore = details.latest_score;
  const latestAudit = details.latest_audit;
  const latestWriter = details.latest_writer;

  const reportUrl = (
    `${API_URL}/reports/companies/`
    + `${company.id}/latest.pdf`
  );

  return (
    <div className="details">
      <h2>{company.name}</h2>

      {latestAudit && (
        <a
          className="pdf-button"
          href={reportUrl}
          target="_blank"
          rel="noreferrer"
        >
          📄 Télécharger le rapport PDF
        </a>
      )}

      <p>
        <strong>📍 Ville :</strong>{" "}
        {company.city || "Non renseignée"}
      </p>

      <p>
        <strong>🏢 Secteur :</strong>{" "}
        {company.sector || "Non renseigné"}
      </p>

      <p>
        <strong>📞 Téléphone :</strong>{" "}
        {company.phone || "Non renseigné"}
      </p>

      <p>
        <strong>✉️ Email :</strong>{" "}
        {company.email || "Non renseigné"}
      </p>

      <p>
        <strong>🌐 Site :</strong>{" "}
        {company.website ? (
          <a
            href={company.website}
            target="_blank"
            rel="noreferrer"
          >
            Voir le site
          </a>
        ) : (
          "Aucun site connu"
        )}
      </p>

      <hr />

      <section className="details-section">
        <h3>📊 Dernier résultat</h3>

        {latestScore ? (
          <>
            <p>
              <strong>Score commercial :</strong>{" "}
              {latestScore.global_score}/100
            </p>

            <p>
              <strong>Priorité :</strong>{" "}
              {latestScore.priority}
            </p>

            {latestAudit && (
              <p>
                <strong>Score technique :</strong>{" "}
                {latestAudit.technical_score}/100
              </p>
            )}

            <h4>Résumé</h4>

            <p>{latestScore.summary}</p>

            {!!latestScore.strengths?.length && (
              <>
                <h4>Points forts</h4>

                <ul>
                  {latestScore.strengths.map(
                    (strength, index) => (
                      <li
                        key={`${strength}-${index}`}
                      >
                        {strength}
                      </li>
                    )
                  )}
                </ul>
              </>
            )}

            {!!latestScore.weaknesses?.length && (
              <>
                <h4>Points à améliorer</h4>

                <ul>
                  {latestScore.weaknesses.map(
                    (weakness, index) => (
                      <li
                        key={`${weakness}-${index}`}
                      >
                        {weakness}
                      </li>
                    )
                  )}
                </ul>
              </>
            )}

            {!!latestScore.opportunities?.length && (
              <>
                <h4>Opportunités</h4>

                <ul>
                  {latestScore.opportunities.map(
                    (opportunity, index) => (
                      <li
                        key={`${opportunity}-${index}`}
                      >
                        {opportunity}
                      </li>
                    )
                  )}
                </ul>
              </>
            )}

            {latestScore.recommended_offer && (
              <>
                <h4>Offre recommandée</h4>

                <p>
                  {latestScore.recommended_offer}
                </p>
              </>
            )}
          </>
        ) : (
          <p>
            Aucun audit disponible pour cette
            entreprise.
          </p>
        )}
      </section>

      <EmailCard
        email={latestWriter}
      />

      <HistoryList
        history={details.history}
      />
    </div>
  );
}


export default CompanyDetails;