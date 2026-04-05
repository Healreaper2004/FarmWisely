const API_URL = (window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost")
  ? "http://127.0.0.1:5000"
  : window.location.origin;

/* =========================
   CSFI CALCULATOR
========================= */
const NUTRIENT_RANGES = {
  N:{min:0,max:140},P:{min:0,max:80},K:{min:0,max:500},
  Ca:{min:0,max:3000},Mg:{min:0,max:600},S:{min:0,max:50},
  Zn:{min:0,max:5},Fe:{min:0,max:20},Cu:{min:0,max:3},
  Mn:{min:0,max:10},B:{min:0,max:2},Mo:{min:0,max:0.5},
};

function norm(v,min,max){
  return max===min ? 0 : Math.min(Math.max((v-min)/(max-min),0),1);
}

function calculateCSFI(){
  const ids=["n","p","k","ca","mg","s","zn","fe","cu","mn","b","mo"];
  const keys=["N","P","K","Ca","Mg","S","Zn","Fe","Cu","Mn","B","Mo"];
  const vals={};

  for(let i=0;i<ids.length;i++){
    const raw=document.getElementById(ids[i]+"_val").value;
    if(raw===""||isNaN(raw)){resetCSFI();return;}
    vals[keys[i]]=parseFloat(raw);
  }

  const n={};
  keys.forEach(k=>n[k]=norm(vals[k],NUTRIENT_RANGES[k].min,NUTRIENT_RANGES[k].max));

  const csfi=parseFloat((0.5*((n.N+n.P+n.K)/3)+0.3*((n.Ca+n.Mg+n.S)/3)+0.2*((n.Zn+n.Fe+n.Cu+n.Mn+n.B+n.Mo)/6)).toFixed(4));
  showCSFIResult(csfi);
}

function showCSFIResult(csfi){
  const score=document.getElementById("csfi-score-value");
  const cls=document.getElementById("csfi-score-class");
  const marker=document.getElementById("csfi-bar-marker");

  let label,color;
  if(csfi<0.3){label="Poor";color="#A32D2D";}
  else if(csfi<0.6){label="Moderate";color="#854F0B";}
  else if(csfi<0.8){label="Good";color="#185FA5";}
  else{label="Excellent";color="#3B6D11";}

  score.textContent=csfi.toFixed(2);
  score.style.color=color;
  cls.textContent=label;
  cls.style.color=color;

  marker.style.display="block";
  marker.style.left=(csfi*100)+"%";

  document.getElementById("csfi-use-btn").disabled=false;
  document.getElementById("csfi-use-btn").dataset.csfi=csfi;
}

function resetCSFI(){
  document.getElementById("csfi-score-value").textContent="—";
  document.getElementById("csfi-score-class").textContent="Fill all values";
}

function useCSFI(){
  const csfi=document.getElementById("csfi-use-btn").dataset.csfi;
  if(!csfi)return;
  document.getElementById("csfi").value=csfi;
}

/* =========================
   PREDICTION
========================= */

function formatFertilizer(f){
  if(!f||!f.quantity)return "N/A";

  if(typeof f.quantity==="object"){
    return Object.entries(f.quantity)
      .map(([k,v])=>`<b>${k}:</b> ${v}`)
      .join("<br>");
  }

  return `<strong>Recommended Dose:</strong> ${f.quantity}`;
}

async function predictFarm(){

  const crop=document.getElementById("crop").value;
  const soil=document.getElementById("soil").value;
  const irrigation=document.getElementById("irrigation").value;
  const season=document.getElementById("season").value;
  const area=document.getElementById("farmArea").value;
  const csfi=document.getElementById("csfi").value;
  const pesticide=document.getElementById("pesticideUsed").value;
  const water=document.getElementById("waterUsage").value;

  const box=document.getElementById("prediction-result");
  const btn=document.getElementById("predictBtn");

  if(!crop||!soil||!irrigation||!season||!area||!csfi||!pesticide||!water){
    box.innerHTML="❌ Fill all fields";
    return;
  }

  const data={
    crop_type:crop,
    soil_type:soil,
    irrigation_type:irrigation,
    season:season,
    farm_area:Number(area),
    csfi:Number(csfi),
    pesticide_used:pesticide,
    water_usage:Number(water)
  };

  btn.disabled=true;
  btn.innerText="Predicting...";
  box.classList.remove("hidden");
  box.innerHTML="⏳ Analysing your farm data...";

  try{
    const res=await fetch(`${API_URL}/predict`,{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(data)
    });

    const result=await res.json();
    console.log("API Response:", result);

    const fert = result?.recommendations?.fertilizer || {};
    const rec  = result?.recommendations || {};
    const metrics = result?.metrics || {};

    // ✅ FIXED CSFI (outside template)
    const csfiNum = Number(csfi);
    let csfiLabel = csfiNum < 0.3 ? "Poor" :
                    csfiNum < 0.6 ? "Moderate" :
                    csfiNum < 0.8 ? "Good" : "Excellent";

    box.innerHTML = `
      <h3>🌾 Predicted Yield</h3>
      <p><b>${(result.predicted_yield||0).toFixed(2)} tons</b></p>
      <p style="font-size:0.85em;color:#666;">
        Case saved as <code>${result.case_id || "N/A"}</code>
      </p>

      <h3>🌱 Fertility Status</h3>
      <p><strong>CSFI:</strong> ${csfiNum.toFixed(2)} (${csfiLabel})</p>

      <h3>🌱 Fertilizer Recommendation</h3>
      <p><strong>${fert.name || "N/A"}</strong></p>
      <p>${formatFertilizer(fert)}</p>

      <h3>💧 Water Strategy</h3>
      <p>${rec.water_usage || "N/A"}</p>
      ${Number(water) > 1000 ? `<p style="color:#c0392b;">⚠ Excess water usage detected. Reduce irrigation.</p>` : ""}

      <h3>🔁 Recommended Next Crop</h3>
      <p><strong>${rec.next_crop || "N/A"}</strong></p>

      <h3>📊 Farm Metrics</h3>
      <table style="width:100%;font-size:0.9em;">
        <tr><td>WPI</td><td>${metrics.WPI ?? "N/A"}</td></tr>
        <tr><td>NES</td><td>${metrics.NES ?? "N/A"}</td></tr>
        <tr>
          <td>SRS</td>
          <td style="color:${metrics.SRS > 0.6 ? '#c0392b' : '#27ae60'}">
            ${metrics.SRS ?? "N/A"}
          </td>
        </tr>
      </table>
    `;

    if (result.case_id) {
      box.innerHTML += `
        <div style="margin-top:15px;padding:12px;border-top:1px solid #ddd;">
          <h3>👍 Was this recommendation useful?</h3>

          <button style="margin-right:10px;padding:6px 12px;border-radius:6px;background:#2e7d32;color:white;border:none;"
            onclick="sendFeedback('${result.case_id}', true)">👍 Yes</button>

          <button style="padding:6px 12px;border-radius:6px;background:#c62828;color:white;border:none;"
            onclick="sendFeedback('${result.case_id}', false)">👎 No</button>

          <br><br>

          <label>Rate (1–5):</label>
          <input type="number" id="rating" min="1" max="5" style="width:60px;margin:0 10px;">
          <button onclick="sendRating('${result.case_id}')">Submit</button>
        </div>
      `;
    }

    // 🧠 CBR insight
    if(result.cbr){
      box.innerHTML += `
        <div style="background:#e8f5e9;padding:10px;border-radius:8px;margin-top:10px;">
          🧠 Based on ${result.cbr.cases_used} similar farmer cases
        </div>
      `;
    }

  }catch(e){
    console.error(e);
    box.innerHTML="❌ Server error";
  }

  btn.disabled=false;
  btn.innerText="Predict Yield";
}

/* =========================
   FEEDBACK
========================= */

async function sendFeedback(caseId, useful) {
  try {
    await fetch(`${API_URL}/feedback`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({case_id: caseId, useful})
    });

    document.getElementById("prediction-result").innerHTML += 
    `<p style="color:green;">✔ Feedback recorded</p>`;
  } catch (e) {
    alert("❌ Failed to save feedback");
  }
}

async function sendRating(caseId) {
  const rating = document.getElementById("rating").value;

  if (!rating || rating < 1 || rating > 5) {
    alert("Enter rating between 1–5");
    return;
  }

  try {
    await fetch(`${API_URL}/feedback`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({case_id: caseId, rating: Number(rating)})
    });

    alert("⭐ Rating submitted!");
  } catch (e) {
    alert("❌ Failed to submit rating");
  }
}

/* =========================
   COMMON FERTILIZER INFO
========================= */

const fertilizerInfo = { 

  rice: `
    <h4>🌾 Rice (Paddy)</h4> 
    <ul> 
      <li><strong>Nitrogen (N):</strong> Urea (46% N) applied in 3 split doses (basal, tillering, panicle stage); Ammonium Sulphate used in alkaline soils</li> 
      <li><strong>Phosphorus (P):</strong> DAP (18:46:0) or SSP applied at transplanting</li> 
      <li><strong>Potassium (K):</strong> MOP improves grain filling and disease resistance</li> 
      <li><strong>Micronutrients:</strong> Zinc Sulphate (ZnSO₄) 5–10 kg/acre</li> 
      <li><strong>Note:</strong> High nitrogen-demand crop</li> 
    </ul>
  `, 

  wheat: `
    <h4>🌾 Wheat</h4> 
    <ul> 
      <li><strong>Nitrogen (N):</strong> Urea at CRI stage</li> 
      <li><strong>Phosphorus (P):</strong> DAP at sowing</li> 
      <li><strong>Potassium (K):</strong> MOP improves grain quality</li> 
      <li><strong>Complex:</strong> NPK (12:32:16)</li> 
      <li><strong>Micronutrients:</strong> Zinc required</li> 
    </ul>
  `, 

  maize: `
    <h4>🌽 Maize (Corn)</h4> 
    <ul> 
      <li><strong>Nitrogen (N):</strong> Urea at knee-high stage</li> 
      <li><strong>Phosphorus (P):</strong> DAP for root growth</li> 
      <li><strong>Potassium (K):</strong> MOP for cob development</li> 
      <li><strong>Complex:</strong> NPK 20:10:10</li> 
      <li><strong>Micronutrients:</strong> Zinc + Boron</li> 
    </ul>
  `, 

  soybean: `
    <h4>🌱 Soybean</h4> 
    <ul> 
      <li><strong>Nitrogen:</strong> Low (nitrogen fixation)</li> 
      <li><strong>Phosphorus:</strong> DAP/SSP for nodulation</li> 
      <li><strong>Potassium:</strong> MOP for seed filling</li> 
      <li><strong>Sulphur:</strong> Gypsum improves protein</li> 
      <li><strong>Biofertilizers:</strong> Rhizobium</li> 
    </ul>
  `

};

function updateFertilizerInfo(crop) {
  const container = document.getElementById("fertilizer-content");
  if (!container) return;
  container.innerHTML = fertilizerInfo[crop];
}

/* =========================
   DYNAMIC NUTRIENT TABLE
========================= */

const nutrientData = {
  rice: [
    ["N (Nitrogen)", "<25", "25–50", ">50"],
    ["P (Phosphorus)", "<10", "10–25", ">25"],
    ["K (Potassium)", "<110", "110–280", ">280"],
    ["Ca", "<500", "500–1500", ">1500"],
    ["Mg", "<60", "60–200", ">200"],
    ["S", "<5", "5–20", ">20"],
    ["Zn", "<0.5", "0.5–1.5", ">1.5"],
    ["Fe", "<2", "2–5", ">5"],
    ["Cu", "<0.2", "0.2–0.8", ">0.8"],
    ["Mn", "<1", "1–3", ">3"],
    ["B", "<0.2", "0.2–0.6", ">0.6"],
    ["Mo", "<0.05", "0.05–0.2", ">0.2"]
  ],

  wheat: [
    ["N", "<20", "20–45", ">45"],
    ["P", "<8", "8–20", ">20"],
    ["K", "<100", "100–250", ">250"],
    ["Ca", "<400", "400–1200", ">1200"],
    ["Mg", "<50", "50–150", ">150"],
    ["S", "<4", "4–15", ">15"],
    ["Zn", "<0.5", "0.5–1.2", ">1.2"],
    ["Fe", "<2", "2–4", ">4"],
    ["Cu", "<0.2", "0.2–0.6", ">0.6"],
    ["Mn", "<1", "1–2.5", ">2.5"],
    ["B", "<0.2", "0.2–0.5", ">0.5"],
    ["Mo", "<0.05", "0.05–0.15", ">0.15"]
  ],

  maize: [
    ["N", "<25", "25–60", ">60"],
    ["P", "<10", "10–30", ">30"],
    ["K", "<120", "120–300", ">300"],
    ["Ca", "<500", "500–1400", ">1400"],
    ["Mg", "<60", "60–180", ">180"],
    ["S", "<5", "5–20", ">20"],
    ["Zn", "<0.5", "0.5–1.5", ">1.5"],
    ["Fe", "<2", "2–5", ">5"],
    ["Cu", "<0.2", "0.2–0.7", ">0.7"],
    ["Mn", "<1", "1–3", ">3"],
    ["B", "<0.2", "0.2–0.6", ">0.6"],
    ["Mo", "<0.05", "0.05–0.2", ">0.2"]
  ],

  soybean: [
    ["N", "<15", "15–40", ">40"],
    ["P", "<10", "10–25", ">25"],
    ["K", "<100", "100–250", ">250"],
    ["Ca", "<400", "400–1200", ">1200"],
    ["Mg", "<50", "50–150", ">150"],
    ["S", "<5", "5–15", ">15"],
    ["Zn", "<0.5", "0.5–1.2", ">1.2"],
    ["Fe", "<2", "2–4", ">4"],
    ["Cu", "<0.2", "0.2–0.6", ">0.6"],
    ["Mn", "<1", "1–2.5", ">2.5"],
    ["B", "<0.2", "0.2–0.5", ">0.5"],
    ["Mo", "<0.05", "0.05–0.15", ">0.15"]
  ]
};

function updateTable(crop) {
  const tableBody = document.getElementById("csfi-table-body");
  if (!tableBody) return;

  tableBody.innerHTML = "";

  nutrientData[crop].forEach(row => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${row[0]}</td>
      <td>${row[1]}</td>
      <td>${row[2]}</td>
      <td>${row[3]}</td>
      <td>mg/kg</td>
    `;

    tableBody.appendChild(tr);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  // Fertilizer
  const fertSelect = document.getElementById("fertCropSelect");
  const cropSelect = document.getElementById("crop");

  if (fertSelect) {
    fertSelect.addEventListener("change", function () {
      updateFertilizerInfo(this.value);
    });
    updateFertilizerInfo("rice");
  }

  if (cropSelect && fertSelect) {
    cropSelect.addEventListener("change", function () {
      const value = this.value.toLowerCase();
      updateFertilizerInfo(value);
      fertSelect.value = value;
    });
  }

  // ✅ Nutrient table FIXED
  const tableCrop = document.getElementById("cropSelect");

  if (tableCrop) {
    // Default load
    updateTable("rice");

    tableCrop.addEventListener("change", function () {
      updateTable(this.value);
    });
  }

});