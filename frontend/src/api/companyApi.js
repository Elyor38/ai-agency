const API_URL = "http://127.0.0.1:8000";

export async function getCompanies() {
    const response = await fetch(`${API_URL}/companies`);

    if (!response.ok) {
        throw new Error("Impossible de récupérer les entreprises.");
    }

    return await response.json();
}