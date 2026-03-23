🌱 FarmWisely – AI-Powered Farming Intelligence Platform

FarmWisely is an intelligent full-stack web application that helps farmers optimize crop yield using machine learning, soil fertility analysis, and sustainability metrics. It combines predictive modeling with agronomic insights to deliver real-time recommendations for better farming decisions.

🚀 Features

🌾 Core Capabilities

📊 ML-Based Yield Prediction – Predict crop yield using trained machine learning model based on farm conditions  
🧪 CSFI Calculator (Soil Fertility Index) – Compute soil fertility using 12 nutrients (macro + micro)  
🌿 Smart Fertilizer Recommendations – Rule-based fertilizer suggestions based on crop, soil, and season  
💧 Water Usage Strategy – Optimized irrigation recommendations  
🔁 Crop Rotation Suggestions – Intelligent next crop recommendations for sustainable farming  
📈 Sustainability Metrics – Advanced analytics for farm efficiency  

📊 Metrics Explained

Metric	Description
WPI (Water Productivity Index)	Yield per unit water used
NES (Nutrient Efficiency Score)	Yield per soil fertility unit (CSFI)
III (Input Intensity Index)	Input load per acre (fertilizer + pesticide)
SRS (Sustainability Risk Score)	Environmental risk based on inputs

🧠 Tech Stack

Frontend: HTML5, CSS3, JavaScript (interactive UI + CSFI calculator)  
Backend: Python (Flask REST API)  
ML Model: Scikit-learn pipeline (trained on agronomic dataset)  
Database: MongoDB (case storage + analytics)  
Architecture: Modular full-stack system (frontend + backend + DB)  

🆕 Key Highlights (2025 Version)

🧪 CSFI Integration: Soil fertility modeled using 12 nutrients with weighted scoring  
📊 Explainable Metrics: WPI, NES, III, SRS provide transparency beyond prediction  
🔐 Privacy-Aware Storage: Farmer data anonymized before storing cases  
⚙️ Rule + ML Hybrid System: Combines machine learning predictions with domain rules  
🌍 Realistic Agronomic Modeling: Yield influenced by farm area, water, and soil conditions  

⚙️ Getting Started (Local Setup)

# 1. Clone the repository
git clone https://github.com/Healreaper2004/FarmWisely.git
cd FarmWisely

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# or
source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add environment variables
# Create a .env file and add:
MONGO_URI=your_mongodb_connection_string

# 5. Run backend
python -m backend.app

# 6. Open frontend
Open frontend/index.html in browser

🤀 File Structure

FarmWisely/
│
├── backend/
│   ├── app.py                  # Flask API
│   ├── rules/                  # Fertilizer + recommendation logic
│   ├── services/               # Metrics + utilities
│   ├── privacy/                # Anonymization logic
│   ├── case_engine/            # Case builder
│
├── frontend/
│   ├── index.html              # Main UI
│   ├── style.css               # Styling
│   ├── script.js               # Frontend logic + CSFI calculator
│   └── hero.jpg                # UI assets
│
├── db/
│   └── mongo.py                # MongoDB connection
│
├── requirements.txt
└── README.md

🔐 Environment Variables

Variable	Description
MONGO_URI	MongoDB connection string

⚠️ Do NOT push .env file to GitHub

💻 Example Workflow

1. Enter farm details (crop, soil, irrigation, season)
2. Calculate CSFI using soil nutrients OR enter manually
3. Get predicted yield from ML model
4. View sustainability metrics (WPI, NES, III, SRS)
5. Receive fertilizer, irrigation, and crop rotation recommendations
6. Case stored anonymously for future insights

🌐 Future Enhancements

📊 Dashboard for farm analytics and trends  
🌍 Weather + region-based prediction integration  
📱 Mobile-friendly progressive web app  
🤖 AI chatbot for farming assistance  
📡 Real-time advisory system for farmers  

👨‍💻 Author

Ayush Arya