async function checkServer() {
  const statusEl = document.getElementById("server-status");
  try {
    const response = await fetch("/api/health");
    const data = await response.json();
    statusEl.textContent = `Server status: ${data.status}`;
  } catch (error) {
    statusEl.textContent = "Could not reach the server.";
  }
}

checkServer();