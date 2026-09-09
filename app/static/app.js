const form = document.querySelector("#upload-form");
const input = document.querySelector("#screenplay");
const fileLabel = document.querySelector("#file-label");
const button = document.querySelector("#analyze-button");
const progress = document.querySelector("#progress");
const progressTitle = document.querySelector("#progress-title");
const progressCopy = document.querySelector("#progress-copy");
const errorBox = document.querySelector("#error");
const results = document.querySelector("#results");
const findingsNode = document.querySelector("#findings");
const summaryNode = document.querySelector("#summary");
let currentReport = null;

input.addEventListener("change", () => {
  fileLabel.textContent = input.files[0]?.name || "Text-based PDF, up to 20 MB";
});

const labels = {
  high_attention: "High attention",
  review: "Review",
  clear_signal: "Clear signal",
  insufficient_evidence: "Insufficient evidence",
};

function escapeHtml(value = "") {
  return String(value).replace(/[&<>'"]/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  })[char]);
}

function renderReport(report) {
  currentReport = report;
  document.querySelector("#report-title").textContent = report.screenplay_title;
  const counts = Object.fromEntries(Object.keys(labels).map((key) => [key, 0]));
  report.findings.forEach((item) => { counts[item.status] = (counts[item.status] || 0) + 1; });
  summaryNode.innerHTML = Object.entries(labels).map(([key, label]) =>
    `<div class="metric"><strong>${counts[key] || 0}</strong><span>${label}</span></div>`
  ).join("");
  findingsNode.innerHTML = report.findings.map((item) => {
    const sources = item.sources.length
      ? item.sources.map((source) => `<li class="source"><a href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.title)}</a>${source.excerpt ? ` — ${escapeHtml(source.excerpt)}` : ""}</li>`).join("")
      : '<li class="source">No reliable source was returned.</li>';
    const limitations = item.limitations?.length
      ? `<p class="limitations"><strong>Limitations:</strong> ${item.limitations.map(escapeHtml).join("; ")}</p>` : "";
    return `<article class="finding">
      <div class="finding-top"><div><h3>${escapeHtml(item.reference_text)}</h3><p class="meta">${escapeHtml(item.scene_or_page)} · ${item.categories.map(escapeHtml).join(", ")} · ${escapeHtml(item.confidence)} confidence</p></div><span class="badge ${escapeHtml(item.status)}">${labels[item.status] || escapeHtml(item.status)}</span></div>
      <p class="context">“${escapeHtml(item.script_context)}”</p>
      <p>${escapeHtml(item.rationale)}</p>
      <p class="recommendation"><strong>Next action:</strong> ${escapeHtml(item.recommended_action)}</p>
      <details><summary>Sources and research query</summary><p class="meta">Query: ${escapeHtml(item.search_query)}</p><ul>${sources}</ul></details>
      ${limitations}
    </article>`;
  }).join("");
  document.querySelector("#disclaimer").textContent = report.disclaimer;
  results.classList.remove("hidden");
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!input.files[0]) return;
  errorBox.classList.add("hidden");
  results.classList.add("hidden");
  progress.classList.remove("hidden");
  button.disabled = true;
  button.textContent = "Analyzing…";
  progressTitle.textContent = "Reading screenplay";
  progressCopy.textContent = "Gemini is identifying references and their scene context.";
  const timer = setTimeout(() => {
    progressTitle.textContent = "Researching references";
    progressCopy.textContent = "The ADK agent is calling Parallel Search for current evidence.";
  }, 3500);

  try {
    const body = new FormData();
    body.append("file", input.files[0]);
    const response = await fetch("/api/analyze", { method: "POST", body });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Analysis failed.");
    renderReport(payload);
  } catch (error) {
    errorBox.textContent = error.message;
    errorBox.classList.remove("hidden");
  } finally {
    clearTimeout(timer);
    progress.classList.add("hidden");
    button.disabled = false;
    button.textContent = "Analyze screenplay";
  }
});

document.querySelector("#download-button").addEventListener("click", () => {
  if (!currentReport) return;
  const blob = new Blob([JSON.stringify(currentReport, null, 2)], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "script-sentinel-report.json";
  link.click();
  URL.revokeObjectURL(link.href);
});

