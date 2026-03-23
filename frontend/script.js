const API_URL = (window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost")
  ? "http://127.0.0.1:5000"
  : window.location.origin;

/* ═══════════════════════════════════════════════════════
   CSFI CALCULATOR
   Nutrient min/max from training dataset ranges
════════════════════════════════════════════════════════ */
const NUTRIENT_RANGES = {
  N:  { min: 0, max: 140  },
  P:  { min: 0, max: 80   },
  K:  { min: 0, max: 500  },
  Ca: { min: 0, max: 3000 },
  Mg: { min: 0, max: 600  },
  S:  { min: 0, max: 50   },
  Zn: { min: 0, max: 5    },
  Fe: { min: 0, max: 20   },
  Cu: { min: 0, max: 3    },
  Mn: { min: 0, max: 10   },
  B:  { min: 0, max: 2    },
  Mo: { min: 0, max: 0.5  },
};

function norm(value, min, max) {
  if (max === min) return 0;
  return Math.min(Math.max((value - min) / (max - min), 0), 1);
}

function calculateCSFI() {
  const fieldIds = ["n","p","k","ca","mg","s","zn","fe","cu","mn","b","mo"];
  const keys     = ["N","P","K","Ca","Mg","S","Zn","Fe","Cu","Mn","B","Mo"];

  const vals = {};
  for (let i = 0; i < fieldIds.length; i++) {
    const raw = document.getElementById(fieldIds[i] + "_val").value;
    if (raw === "" || isNaN(raw)) { resetCSFI(); return; }
    vals[keys[i]] = parseFloat(raw);
  }

  // Normalise each nutrient to [0,1]
  const n = {};
  for (const key of keys) {
    n[key] = norm(vals[key], NUTRIENT_RANGES[key].min, NUTRIENT_RANGES[key].max);
  }

  // CSFI formula — exact match to notebook
  const I_primary   = (n["N"] + n["P"] + n["K"]) / 3;
  const I_secondary = (n["Ca"] + n["Mg"] + n["S"]) / 3;
  const I_micro     = (n["Zn"] + n["Fe"] + n["Cu"] + n["Mn"] + n["B"] + n["Mo"]) / 6;
  const csfi        = parseFloat((0.50 * I_primary + 0.30 * I_secondary + 0.20 * I_micro).toFixed(4));

  showCSFIResult(csfi);
}

function showCSFIResult(csfi) {
  const scoreEl  = document.getElementById("csfi-score-value");
  const classEl  = document.getElementById("csfi-score-class");
  const markerEl = document.getElementById("csfi-bar-marker");
  const boxEl    = document.getElementById("csfi-result-box");
  const useBtn   = document.getElementById("csfi-use-btn");

  let label, color;
  if      (csfi < 0.30) { label = "Poor — urgent soil attention needed";    color = "#A32D2D"; }
  else if (csfi < 0.60) { label = "Moderate — consider improvement";        color = "#854F0B"; }
  else if (csfi < 0.80) { label = "Good — healthy soil";                    color = "#185FA5"; }
  else                  { label = "Excellent — optimal fertility";           color = "#3B6D11"; }

  scoreEl.textContent = csfi.toFixed(2);
  scoreEl.style.color = color;
  classEl.textContent = label;
  classEl.style.color = color;

  markerEl.style.display = "block";
  markerEl.style.left    = (csfi * 100) + "%";

  boxEl.classList.add("active");

  useBtn.disabled       = false;
  useBtn.dataset.csfi   = csfi.toFixed(4);
}

function resetCSFI() {
  document.getElementById("csfi-score-value").textContent = "—";
  document.getElementById("csfi-score-value").style.color = "#2e4f1f";
  document.getElementById("csfi-score-class").textContent = "Fill in all 12 values above";
  document.getElementById("csfi-score-class").style.color = "#777";
  document.getElementById("csfi-bar-marker").style.display = "none";
  document.getElementById("csfi-result-box").classList.remove("active");
  document.getElementById("csfi-use-btn").disabled = true;
}

function useCSFI() {
  const csfi = document.getElementById("csfi-use-btn").dataset.csfi;
  if (!csfi) return;

  // Fill CSFI field in prediction form
  const input = document.getElementById("csfi");
  input.value = csfi;

  // Flash green border to confirm
  input.style.border     = "2px solid #2e4f1f";
  input.style.background = "#f2f8ee";
  setTimeout(() => {
    input.style.border     = "";
    input.style.background = "";
  }, 2000);

  // Scroll to Step 2
  document.querySelector(".prediction").scrollIntoView({ behavior: "smooth" });

  // Button feedback
  const btn      = document.getElementById("csfi-use-btn");
  const original = btn.innerText;
  btn.innerText  = "✅ Filled in Step 2!";
  setTimeout(() => { btn.innerText = original; }, 2500);
}

/* ═══════════════════════════════════════════════════════
   PREDICTION
════════════════════════════════════════════════════════ */
async function predictFarm() {
  const crop       = document.getElementById("crop").value;
  const soil       = document.getElementById("soil").value;
  const irrigation = document.getElementById("irrigation").value;
  const season     = document.getElementById("season").value;
  const area       = document.getElementById("farmArea").value;
  const csfi       = document.getElementById("csfi").value;
  const pesticide  = document.getElementById("pesticideUsed").value;
  const water      = document.getElementById("waterUsage").value;

  const resultBox = document.getElementById("prediction-result");
  const button    = document.getElementById("predictBtn");

  if (button.disabled) return;

  if (!crop || !soil || !irrigation || !season || !area || !csfi || !pesticide || !water) {
    resultBox.classList.remove("hidden");
    resultBox.innerHTML = "<p style='color:red'>❌ Please fill all fields</p>";
    return;
  }

  if (isNaN(area) || Number(area) <= 0) {
    resultBox.classList.remove("hidden");
    resultBox.innerHTML = "<p style='color:red'>❌ Farm area must be a valid positive number</p>";
    return;
  }

  if (isNaN(csfi) || Number(csfi) < 0 || Number(csfi) > 1) {
    resultBox.classList.remove("hidden");
    resultBox.innerHTML = "<p style='color:red'>❌ CSFI must be between 0 and 1</p>";
    return;
  }

  if (isNaN(water) || Number(water) < 0) {
    resultBox.classList.remove("hidden");
    resultBox.innerHTML = "<p style='color:red'>❌ Water usage must be a valid positive number</p>";
    return;
  }

  const data = {
    crop_type:       crop,
    soil_type:       soil,
    irrigation_type: irrigation,
    season:          season,
    farm_area:       Number(area),
    csfi:            Number(csfi),
    pesticide_used:  pesticide,
    water_usage:     Number(water)
  };

  button.disabled  = true;
  button.innerText = "Predicting...";
  resultBox.classList.remove("hidden");
  resultBox.innerHTML = "<p>⏳ Analysing your farm data...</p>";
  resultBox.scrollIntoView({ behavior: "smooth" });

  try {
    const response = await fetch(`${API_URL}/predict`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(data)
    });

    const result = await response.json();

    if (!response.ok) {
      resultBox.innerHTML = `<p style="color:red">❌ ${result.error || "Prediction failed"}</p>`;
      return;
    }

    const fertilizer = result?.recommendations?.fertilizer || {};
    const metrics    = result?.metrics || {};
    const rec        = result?.recommendations || {};

    const tips = rec.improvements && rec.improvements.length > 0
      ? rec.improvements.map(t => `<li>${t}</li>`).join("")
      : "<li>Current practices are optimal 🎉</li>";

    const srs      = Math.min(metrics.SRS ?? 0, 1.0);
    const srsColor = srs > 0.7 ? "#c0392b" : srs > 0.4 ? "#e67e22" : "#27ae60";
    const srsLabel = srs > 0.7 ? "High Risk" : srs > 0.4 ? "Moderate" : "Low Risk";

    const csfiNum = Number(csfi);
    let csfiLabel = "";
    if      (csfiNum < 0.30) csfiLabel = "Poor";
    else if (csfiNum < 0.60) csfiLabel = "Moderate";
    else if (csfiNum < 0.80) csfiLabel = "Good";
    else                     csfiLabel = "Excellent";

    resultBox.innerHTML = `
      <h3>🌾 Predicted Yield</h3>
      <p><strong>${(result.predicted_yield ?? 0).toFixed(2)} tons</strong></p>
      <p style="font-size:0.85em;color:#666;">Case saved as <code>${result.case_id || "N/A"}</code></p>

      <h3>🌱 Fertility Status</h3>
      <p><strong>CSFI:</strong> ${csfiNum.toFixed(2)} (${csfiLabel})</p>

      <h3>🌱 Fertilizer Recommendation</h3>
      <p><strong>${fertilizer.name || "N/A"}</strong> — ${fertilizer.quantity || ""}</p>
      <p><em>${fertilizer.timing || ""}</em></p>

      <h3>💧 Water Strategy</h3>
      <p>${rec.water_usage || "N/A"}</p>

      <h3>🔁 Recommended Next Crop</h3>
      <p><strong>${rec.next_crop || "N/A"}</strong></p>

      <h3>📊 Farm Metrics</h3>
      <table style="width:100%;border-collapse:collapse;font-size:0.9em;">
        <tr><td>Water Productivity (WPI)</td><td><strong>${metrics.WPI ?? "N/A"}</strong></td></tr>
        <tr><td>Nutrient Efficiency (NES)</td><td><strong>${metrics.NES ?? "N/A"}</strong></td></tr>
        <tr><td>Input Intensity (III)</td><td><strong>${metrics.III ?? "N/A"}</strong></td></tr>
        <tr>
          <td>Sustainability Risk (SRS)</td>
          <td><strong style="color:${srsColor}">${srs} — ${srsLabel}</strong></td>
        </tr>
      </table>

      <h3>📈 Improvement Tips</h3>
      <ul>${tips}</ul>
    `;

  } catch (error) {
    resultBox.innerHTML = "<p style='color:red'>❌ Server error. Please try again.</p>";
    console.error(error);
  } finally {
    button.disabled  = false;
    button.innerText = "Predict Yield";
  }
}