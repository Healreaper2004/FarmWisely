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

function norm(v,min,max){return max===min?0:Math.min(Math.max((v-min)/(max-min),0),1)}

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
  if(!f||!f.quantity)return"N/A";
  if(typeof f.quantity==="object"){
    return Object.entries(f.quantity).map(([k,v])=>`<b>${k}:</b> ${v}`).join("<br>");
  }
  return f.quantity;
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
    box.innerHTML="❌ Fill all fields";return;
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
  box.innerHTML="⏳ Analysing...";

  try{
    const res=await fetch(`${API_URL}/predict`,{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(data)
    });

    const result=await res.json();

    /* =========================
       🧠 CASE-BASED RESULT
    ========================= */
    if(result.type==="CBR"){
      const sol=result.recommendation||{};

      box.innerHTML=`
        <h3>🧠 Case-Based Recommendation</h3>
        <p style="color:green;">Based on ${result.cases_used} similar cases</p>
        <p>${result.reason}</p>

        <h3>🌱 Fertilizer</h3>
        <p><b>${sol.fertilizer?.name||"N/A"}</b></p>
        <p>${formatFertilizer(sol.fertilizer)}</p>

        <h3>💧 Irrigation</h3>
        <p>${sol.irrigation_strategy||"N/A"}</p>

        <div style="background:#e8f5e9;padding:10px;border-radius:8px;">
          💡 Based on real anonymized farmer data
        </div>
      `;

      btn.disabled=false;
      btn.innerText="Predict Yield";
      
      if (result.case_id) {
        box.innerHTML += `
          <h3>👍 Was this helpful?</h3>
          <button onclick="sendFeedback('${result.case_id}', true)">👍 Yes</button>
          <button onclick="sendFeedback('${result.case_id}', false)">👎 No</button>
        `;
      }
      
      return;
    }

    /* =========================
       🤖 ML RESULT
    ========================= */
    const fert=result?.recommendations?.fertilizer||{};
    const rec=result?.recommendations||{};

    box.innerHTML=`
      <h3>🤖 AI Prediction</h3>
      <h3>🌾 Yield</h3>
      <p><b>${(result.predicted_yield||0).toFixed(2)} tons</b></p>

      <h3>🌱 Fertilizer</h3>
      <p><b>${fert.name||"N/A"}</b></p>
      <p>${formatFertilizer(fert)}</p>

      <h3>💧 Water</h3>
      <p>${rec.water_usage||"N/A"}</p>

      <h3>🔁 Next Crop</h3>
      <p>${rec.next_crop||"N/A"}</p>
    `;

    if (result.case_id) {
      Box.innerHTML += `
        <h3>👍 Was this recommendation useful?</h3>
        <button onclick="sendFeedback('${result.case_id}', true)">👍 Yes</button>
        <button onclick="sendFeedback('${result.case_id}', false)">👎 No</button>

        <br><br>
        <label>Rate (1–5):</label>
        <input type="number" id="rating" min="1" max="5">
        <button onclick="sendRating('${result.case_id}')">Submit Rating</button>
      `;
    }

  }catch(e){
    box.innerHTML="❌ Server error";
  }

  btn.disabled=false;
  btn.innerText="Predict Yield";
}

async function sendFeedback(caseId, useful) {
  try {
    await fetch(`${API_URL}/feedback`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        case_id: caseId,
        useful: useful
      })
    });

    alert("✅ Feedback saved!");
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
      body: JSON.stringify({
        case_id: caseId,
        rating: Number(rating)
      })
    });

    alert("⭐ Rating submitted!");
  } catch (e) {
    alert("❌ Failed to submit rating");
  }
}