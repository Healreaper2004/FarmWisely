# 🌾 FarmWisely – AI-Powered Smart Farming System

FarmWisely is an intelligent decision-support system that helps farmers optimise crop yield using AI-driven predictions, soil fertility analysis (CSFI), and rule-based agronomic recommendations.

It combines Machine Learning, sustainability metrics, and privacy-preserving data processing to deliver actionable insights for modern agriculture.

---

## 🚀 Features

### 🌿 Core Capabilities

* 📊 **Yield Prediction (ML Model)** – Predicts crop yield based on farm inputs
* 🌱 **CSFI (Soil Fertility Index)** – Quantifies soil health on a scale of 0–1
* 🧠 **Smart Recommendations Engine** – Suggests fertilizer, irrigation, and crop rotation
* 📈 **Advanced Farm Metrics**

  * WPI – Water Productivity Index
  * NES – Nutrient Efficiency Score
  * III – Input Intensity Index
  * SRS – Sustainability Risk Score
* 🔐 **Privacy-Preserving Pipeline**

  * Removes personal data
  * Generalises sensitive values into safe ranges
* 📦 **Case-Based Storage** – Stores anonymised farm cases in MongoDB

---

## 🧠 Tech Stack

* **Frontend**: HTML5, CSS3, JavaScript
* **Backend**: Python (Flask REST API)
* **Machine Learning**: Scikit-learn / Regression Model
* **Database**: MongoDB Atlas
* **Architecture**: Modular (Rules + Metrics + Privacy + Case Engine)

---

## 🆕 Key Innovations

* 🌱 **CSFI-Based Fertility Modeling** (0–1 scale)
* 📊 **Post-Prediction Metrics Layer** (separate from ML)
* 🧠 **Explainable AI Output via Metrics**
* 🔐 **Built-in Data Anonymization**
* ⚙️ **Rule-Based + ML Hybrid System**

---

## 🧮 What is CSFI?

**CSFI (Composite Soil Fertility Index)** combines multiple soil nutrients into a single score between **0 and 1**.

| Range       | Interpretation |
| ----------- | -------------- |
| 0 – 0.30    | Poor           |
| 0.30 – 0.60 | Moderate       |
| 0.60 – 0.80 | Good           |
| 0.80 – 1.00 | Excellent      |

👉 FarmWisely includes a built-in **CSFI Calculator UI** to help users compute this easily.

---

## 🧪 Example Workflow

1. Enter farm details (crop, soil, irrigation, etc.)
2. Calculate or input CSFI
3. Click **Predict Yield**
4. Get:

   * Predicted yield
   * Fertility status
   * Recommendations
   * Sustainability metrics
   * Next crop suggestion

---

## ⚙️ Getting Started (Local Setup)

```bash
# 1. Clone repository
git clone https://github.com/Healreaper2004/FarmWisely.git
cd FarmWisely

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# or
source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add MongoDB URI
# Create a .env file and add:
MONGO_URI=your_mongodb_connection_string

# 5. Run backend
python -m backend.app
```

---

## 🌐 Run Application

* Backend: http://127.0.0.1:5000
* Frontend: Open `frontend/index.html` in browser

---

## 📁 File Structure

```text
FarmWisely/
│
├── backend/
│   ├── app.py                  # Flask API
│   ├── rules/                  # Fertilizer + recommendation logic
│   ├── services/               # Metrics computation
│   ├── privacy/                # Anonymization engine
│   ├── case_engine/            # Case builder (Mongo storage)
│
├── frontend/
│   ├── index.html              # Main UI
│   ├── style.css               # Styling
│   ├── script.js               # Logic + CSFI calculator
│   └── hero.jpg                # UI image
│
├── db/
│   └── mongo.py                # MongoDB connection
│
├── requirements.txt
└── README.md
```

---

## 📊 Metrics Explanation

* **WPI (Water Productivity Index)**
  Yield per unit water used

* **NES (Nutrient Efficiency Score)**
  Yield per unit soil fertility

* **III (Input Intensity Index)**
  Input usage per acre

* **SRS (Sustainability Risk Score)**
  Measures environmental risk based on inputs

---

## 🔐 Privacy Design

FarmWisely ensures data safety through:

* ❌ Removal of personal identifiers
* 📉 Suppression of extreme values
* 📊 Conversion into range buckets

---

## 💡 Key Insight (For Viva / Interview)

* Yield is primarily influenced by:

  * Farm Area (~49%)
  * Water Usage (~28%)
* CSFI contributes (~6%) → reflects soil health, not total production
* Sustainability is captured via metrics (WPI, NES, SRS)

---

## 🌱 Future Enhancements

* 📡 Weather API integration
* 📊 Farmer dashboard analytics
* 📱 Mobile app version
* 🤖 AI chatbot for farm advisory

---

## 👨‍💻 Author

**Ayush Arya**

---

