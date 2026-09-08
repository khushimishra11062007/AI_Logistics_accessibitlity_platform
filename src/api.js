export async function checkBackend() {
  const response = await fetch("http://localhost:8000/api/health");

  if (!response.ok) {
    throw new Error("Backend is not reachable");
  }

  return await response.json();
}