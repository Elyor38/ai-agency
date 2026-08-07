import { useState } from "react";


function EmailCard({ email }) {
  const [copied, setCopied] = useState(false);

  if (!email) {
    return (
      <section className="details-section">
        <h3>✉️ Email commercial</h3>
        <p>Aucun email disponible.</p>
      </section>
    );
  }

  async function handleCopy() {
    const fullEmail = [
      `Objet : ${email.email_subject}`,
      "",
      email.email_body,
    ].join("\n");

    try {
      await navigator.clipboard.writeText(
        fullEmail
      );

      setCopied(true);

      window.setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch (error) {
      console.error(
        "Impossible de copier l'email.",
        error
      );
    }
  }

  return (
    <section className="details-section">
      <h3>✉️ Email commercial</h3>

      <p>
        <strong>Objet :</strong>{" "}
        {email.email_subject}
      </p>

      <pre className="email-preview">
        {email.email_body}
      </pre>

      {email.commercial_offer && (
        <>
          <h4>Offre commerciale</h4>
          <p>{email.commercial_offer}</p>
        </>
      )}

      {email.call_to_action && (
        <>
          <h4>Appel à l'action</h4>
          <p>{email.call_to_action}</p>
        </>
      )}

      <button
        type="button"
        className="details-button"
        onClick={handleCopy}
      >
        {copied
          ? "Email copié ✓"
          : "Copier l'email"}
      </button>
    </section>
  );
}


export default EmailCard;