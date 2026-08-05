const API_URL = "http://127.0.0.1:8000";

export async function getDashboardStats() {
    const response = await fetch(`${API_URL}/dashboard/stats`);

    if (!response.ok) {
        throw new Error("Impossible de récupérer les statistiques.");
    }

    return await response.json();
}