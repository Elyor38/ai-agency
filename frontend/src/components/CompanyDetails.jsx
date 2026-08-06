function CompanyDetails({ details }) {

    if (!details) {
        return null;
    }

    return (

        <div className="details">

            <h2>{details.company.name}</h2>

            <p>
                <strong>📍 Ville :</strong>{" "}
                {details.company.city}
            </p>

            <p>
                <strong>🌐 Site :</strong>{" "}
                <a
                    href={details.company.website}
                    target="_blank"
                    rel="noreferrer"
                >
                    {details.company.website}
                </a>
            </p>

            <hr />

            <h3>Dernier audit</h3>

            {details.latest_score ? (

                <>

                    <p>

                        <strong>Score :</strong>{" "}

                        {details.latest_score.global_score}/100

                    </p>

                    <p>

                        <strong>Priorité :</strong>{" "}

                        {details.latest_score.priority}

                    </p>

                    <p>

                        <strong>Résumé :</strong>

                    </p>

                    <p>

                        {details.latest_score.summary}

                    </p>

                </>

            ) : (

                <p>Aucun audit disponible.</p>

            )}

            <hr />

            <h3>Dernier email</h3>

            {details.latest_writer ? (

                <>

                    <p>

                        <strong>Objet</strong>

                    </p>

                    <p>

                        {details.latest_writer.email_subject}

                    </p>

                    <p>

                        <strong>Message</strong>

                    </p>

                    <textarea
                        readOnly
                        value={
                            details.latest_writer.email_body
                        }
                        rows={12}
                        style={{
                            width: "100%",
                        }}
                    />

                </>

            ) : (

                <p>Aucun email généré.</p>

            )}

        </div>

    );

}

export default CompanyDetails;