function formatDate(value) {
  if (!value) {
    return "Date inconnue";
  }

  return new Intl.DateTimeFormat(
    "fr-FR",
    {
      dateStyle: "medium",
      timeStyle: "short",
    }
  ).format(new Date(value));
}


function HistoryList({ history }) {
  if (!history?.length) {
    return (
      <section className="details-section">
        <h3>Historique</h3>
        <p>Aucun historique disponible.</p>
      </section>
    );
  }

  return (
    <section className="details-section">
      <h3>Historique</h3>

      <div className="history-list">
        {history.map((item) => (
          <article
            className="history-item"
            key={item.audit.id}
          >
            <p>
              <strong>
                {formatDate(
                  item.audit.created_at
                )}
              </strong>
            </p>

            <p>
              Score technique :{" "}
              {item.audit.technical_score}/100
            </p>

            {item.score && (
              <>
                <p>
                  Score commercial :{" "}
                  {item.score.global_score}/100
                </p>

                <p>
                  Priorité :{" "}
                  {item.score.priority}
                </p>
              </>
            )}

            {item.writer && (
              <p>
                Email :{" "}
                {item.writer.email_subject}
              </p>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}


export default HistoryList;