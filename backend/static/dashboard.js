// dashboard.js

async function loadData() {
  const res = await fetch("/events");
  const data = await res.json();

  // stats
  document.getElementById("total").textContent = data.length;
  document.getElementById("countries").textContent =
    new Set(data.map(e => e.country)).size;
  document.getElementById("trackers").textContent =
    data.filter(e => e.category !== "first-party").length;

  const tbody = document.getElementById("rows");
  tbody.innerHTML = "";

  // newest first
  data.slice().reverse().forEach(e => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${e.domain}</td>

      <td>
        <span class="badge ${e.category}">
          ${e.category}
        </span>
      </td>

      <td>
        <span class="risk ${e.risk.toLowerCase()}">
          ${e.risk}
        </span>
      </td>

      <td>${e.country}</td>
      <td>${e.city}</td>
      <td>${e.org}</td>
      <td>${new Date(e.timestamp).toLocaleTimeString()}</td>
    `;

    tbody.appendChild(tr);
  });
}

async function loadPrivacyScore() {
  const res = await fetch("/privacy-score");
  const data = await res.json();
  document.getElementById("privacyScore").textContent = data.score;
}

// refresh loops
setInterval(loadData, 1500);
setInterval(loadPrivacyScore, 2000);

// initial load
loadData();
loadPrivacyScore();
function exportReport() {
  // open export endpoint in new tab
  window.open("/export", "_blank");
}
