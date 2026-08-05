const API_URL = "http://127.0.0.1:8000";

export async function runCompanyWorkflow(companyId) {
  const response = await fetch(
    `${API_URL}/workflow/companies/${companyId}`,
    {
      method: "POST",
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Impossible de lancer le workflow."
    );
  }

  return data;
}