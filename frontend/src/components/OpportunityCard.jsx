const SERVICE_LABELS = {
  website_creation: "Création de site",
  website_redesign: "Refonte du site",
  seo_local: "Visibilité locale",
  google_business: "Présence sur Google",
  social_media: "Réseaux sociaux",
  conversion_optimization: "Optimisation des réservations",
  reputation_management: "Réputation en ligne",
  no_priority: "Aucune priorité commerciale",
};


function OpportunityCard({ opportunity }) {
  if (!opportunity) {
    return null;
  }

  const confidence = Math.round(
    opportunity.confidence * 100
  );

  return (
    <section className="details-section">
      <h3>🎯 Opportunité recommandée</h3>

      <p className="opportunity-service">
        {SERVICE_LABELS[opportunity.service]
          || opportunity.service}
      </p>

      <p>
        <strong>Confiance :</strong>{" "}
        {confidence} %
      </p>

      <h4>Pourquoi cette recommandation ?</h4>
      <p>{opportunity.reason}</p>

      <h4>Problème identifié</h4>
      <p>{opportunity.business_problem}</p>

      <h4>Action recommandée</h4>
      <p>{opportunity.recommended_action}</p>

      <h4>Angle commercial</h4>
      <p>{opportunity.sales_angle}</p>
    </section>
  );
}


export default OpportunityCard;