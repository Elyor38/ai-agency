function WebsiteOfferCard({ offer }) {
  if (!offer) {
    return null;
  }

  return (
    <section className="details-section">
      <h3>🌐 Proposition de création de site</h3>

      <p className="opportunity-service">
        {offer.offer_title}
      </p>

      <h4>Pages recommandées</h4>

      <ul>
        {offer.recommended_pages.map(
          (page, index) => (
            <li key={`${page}-${index}`}>
              {page}
            </li>
          )
        )}
      </ul>

      <h4>Fonctionnalités recommandées</h4>

      <ul>
        {offer.recommended_features.map(
          (feature, index) => (
            <li key={`${feature}-${index}`}>
              {feature}
            </li>
          )
        )}
      </ul>

      <h4>Bénéfices pour l'entreprise</h4>

      <ul>
        {offer.business_benefits.map(
          (benefit, index) => (
            <li key={`${benefit}-${index}`}>
              {benefit}
            </li>
          )
        )}
      </ul>
    </section>
  );
}


export default WebsiteOfferCard;