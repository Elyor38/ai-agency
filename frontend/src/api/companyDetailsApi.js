const API_URL = "http://127.0.0.1:8000";

export async function getCompanyDetails(companyId) {
    const response = await fetch(
        `${API_URL}/companies/${companyId}/details`
    );

    if (!response.ok) {
        throw new Error(
            "Impossible de récupérer les détails de l'entreprise."
        );
    }

    return await response.json();
}