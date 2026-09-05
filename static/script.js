// script.js
// Handles all client-side interaction: building an expression from button
// presses, calling the Flask API to evaluate it, and rendering history +
// stats returned from the backend.

const expressionLine = document.getElementById("expression-line");
const display = document.getElementById("display");
const keys = document.querySelectorAll(".key");
const nlForm = document.getElementById("nl-form");
const nlInput = document.getElementById("nl-input");
const nlParsed = document.getElementById("nl-parsed");
const historyList = document.getElementById("history-list");
const statsSummary = document.getElementById("stats-summary");
const clearHistoryBtn = document.getElementById("clear-history");

let current = "";

function renderDisplay(text, isError = false) {
  display.textContent = text === "" ? "0" : text;
  display.classList.toggle("error", isError);
}

function updateExpressionLine() {
  expressionLine.textContent = current;
}

async function submitExpression(expression) {
  try {
    const res = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ expression }),
    });
    const data = await res.json();
    if (!data.success) {
      renderDisplay(data.error, true);
      return;
    }
    renderDisplay(String(data.result));
    current = String(data.result);
    updateExpressionLine();
    loadHistory();
    loadStats();
  } catch (err) {
    renderDisplay("Network error", true);
  }
}

keys.forEach((key) => {
  key.addEventListener("click", () => {
    const { action, value } = key.dataset;

    if (action === "clear") {
      current = "";
      expressionLine.textContent = "";
      renderDisplay("");
      return;
    }

    if (action === "backspace") {
      current = current.slice(0, -1);
      updateExpressionLine();
      renderDisplay(current);
      return;
    }

    if (action === "equals") {
      if (current.trim() === "") return;
      submitExpression(current);
      return;
    }

    current += value;
    updateExpressionLine();
    renderDisplay(current);
  });
});

// Let the keyboard drive the calculator too, not just clicks
window.addEventListener("keydown", (e) => {
  if (document.activeElement === nlInput) return; // don't hijack text input

  if (e.key >= "0" && e.key <= "9") {
    current += e.key;
  } else if ("+-*/().%".includes(e.key)) {
    current += e.key;
  } else if (e.key === "Enter" || e.key === "=") {
    if (current.trim() !== "") submitExpression(current);
    return;
  } else if (e.key === "Backspace") {
    current = current.slice(0, -1);
  } else if (e.key === "Escape") {
    current = "";
  } else {
    return;
  }
  updateExpressionLine();
  renderDisplay(current);
});

nlForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = nlInput.value.trim();
  if (!query) return;

  try {
    const res = await fetch("/api/calculate/natural", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();
    if (!data.success) {
      nlParsed.textContent = data.error;
      nlParsed.classList.add("error");
      return;
    }
    nlParsed.classList.remove("error");
    nlParsed.textContent = `Parsed as: ${data.parsed_expression} = ${data.result}`;
    current = String(data.result);
    updateExpressionLine();
    renderDisplay(current);
    nlInput.value = "";
    loadHistory();
    loadStats();
  } catch (err) {
    nlParsed.textContent = "Network error";
    nlParsed.classList.add("error");
  }
});

async function loadHistory() {
  try {
    const res = await fetch("/api/history?limit=10");
    const rows = await res.json();
    historyList.innerHTML = "";
    if (rows.length === 0) {
      historyList.innerHTML = '<li class="h-expr">No calculations yet.</li>';
      return;
    }
    rows.forEach((row) => {
      const li = document.createElement("li");
      const sourceLabel = row.source === "natural_language" ? "NL" : "";
      li.innerHTML = `
        <span class="h-expr">${row.expression} = ${row.result}</span>
        <span class="h-source">${sourceLabel}</span>
      `;
      historyList.appendChild(li);
    });
  } catch (err) {
    // fail silently -- history is a nice-to-have, not critical path
  }
}

async function loadStats() {
  try {
    const res = await fetch("/api/stats");
    const data = await res.json();
    if (data.total_calculations === 0) {
      statsSummary.textContent = "No calculations yet.";
      return;
    }
    const mostUsed = data.most_used_operator || "n/a";
    statsSummary.textContent =
      `Total calculations: ${data.total_calculations}\n` +
      `Most used operator: ${mostUsed}`;
    statsSummary.style.whiteSpace = "pre-line";
  } catch (err) {
    // fail silently
  }
}

clearHistoryBtn.addEventListener("click", async () => {
  await fetch("/api/history", { method: "DELETE" });
  loadHistory();
  loadStats();
});

// Initial load
loadHistory();
loadStats();
