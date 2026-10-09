<div align="center">
  <img src="https://img.shields.io/badge/Water-Security-00B4D8?style=for-the-badge&logo=water&logoColor=white" alt="Water Security" />
  <img src="https://img.shields.io/badge/AI-Powered-FF6B35?style=for-the-badge&logo=artificial-intelligence&logoColor=white" alt="AI Powered" />
  <img src="https://img.shields.io/badge/Real--Time-Monitoring-2E8B57?style=for-the-badge&logo=grafana&logoColor=white" alt="Real-Time Monitoring" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
</div>

<br/>

<div align="center">
  <h1>🌊 AquaShield AI</h1>
  <p><strong>AI-Powered Water Quality Monitoring, Safety Classification & Safe Source Locator Platform</strong></p>
  
  [![React](https://img.shields.io/badge/React-19-20232A?style=flat-square&logo=react&logoColor=61DAFB)](https://reactjs.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
  [![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
  [![Vite](https://img.shields.io/badge/Vite-8.3-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

</div>

---

## 📖 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [ML Engine & Water Quality Model](#-ml-engine--water-quality-model)
- [Installation & Setup](#-installation--setup)
- [Running Tests](#-running-tests)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**AquaShield AI** is an intelligent water security platform combining machine learning, real-time IoT sensor telemetry, geospatial mapping, and community-driven incident reporting to safeguard drinking water.

### 🚀 Highlights
- **Early Hazard Detection**: Predicts contamination risk across pH, Turbidity, TDS, and Temperature.
- **Nearest Safe Source Locator**: Finds the closest verified potable water source with GPS routing.
- **Community Incident Reporting**: Allows citizens to report issues with geo-tags and photo proof.
- **Actionable Guidance**: Translates complex chemical parameters into plain-language drinking advice.

---

## ✨ Key Features

### 🏠 **Interactive Dashboard**
- Real-time parameter stream: pH, Turbidity, TDS, Temperature.
- City-wide water security score and regional safety distribution.
- Interactive safety status banners and quick-action shortcuts.

### 🤖 **AI Water Safety Classifier**
- **4 Key Parameters**: pH (0-14), Turbidity (NTU), TDS (ppm), Temperature (°C).
- **Classification Output**: 
  - 🟢 **Safe** (WHO/EPA compliant for direct consumption)
  - 🟡 **Moderate** (Requires boiling/filtration before use)
  - 🔴 **Dangerous** (Severe chemical or pathogen risk - do not consume)
- **Confidence Scoring & Treatment Advice**: Step-by-step guidance tailored to the detected risk.

### 🗺️ **Safe Source Locator & Map**
- Interactive Leaflet map displaying verified water sources:
  - Springs & Natural Reservoirs
  - Deep Ground Borewells & Wells
  - Municipal Public Tap Stations
  - Accredited Testing Facilities
- Real-time calculation of distance (km) and walking time.
- Direct "Route to Safe Water" navigational path generation.

### 🚨 **Community Reports & Alerts**
- Crowdsourced reporting for industrial runoff, algal blooms, discoloration, and pipe bursts.
- Upvoting and verification workflows.
- Real-time advisory alerts with urgency badges (Advisory, Warning, Critical).

---

## 💻 Tech Stack

### Frontend
- **Framework**: React 19 + Vite 8
- **Styling**: Tailwind CSS
- **Mapping**: Leaflet & React-Leaflet
- **Data Visualization**: Recharts
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Asynchronous Python)
- **Database**: SQLite / PostgreSQL via Async SQLAlchemy 2.0 & Aiosqlite
- **Authentication**: JWT (JSON Web Tokens) with Passlib & Bcrypt
- **API Documentation**: Interactive Swagger UI (`/docs`) & ReDoc (`/redoc`)

### Machine Learning
- **Model**: Scikit-learn Random Forest Classifier
- **Features**: pH, Turbidity (NTU), Total Dissolved Solids (ppm), Temperature (°C)
- **Fallback Engine**: Deterministic WHO & EPA water quality safety rules

---

## 📁 Project Structure

```
AquaShield-AI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── alerts_router.py
│   │   │   ├── analytics_router.py
│   │   │   ├── auth_router.py
│   │   │   ├── predict_router.py
│   │   │   ├── reports_router.py
│   │   │   └── sources_router.py
│   │   ├── services/
│   │   │   ├── alert_service.py
│   │   │   ├── geo_service.py
│   │   │   └── ml_service.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── tests/
│   │   └── test_api.py
│   ├── seed_data.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── ml/
│   ├── dataset.csv
│   ├── model.joblib
│   ├── predict.py
│   └── train.py
├── data/
│   ├── sample_sources.json
│   └── water_quality_training_data.csv
├── requirements.txt
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/predict` | Classify water parameters (pH, turbidity, TDS, temp) |
| `GET`  | `/api/sources` | List all water sources with live quality status |
| `GET`  | `/api/sources/nearby` | Query sources near latitude & longitude |
| `GET`  | `/api/sources/nearest-safe` | Find closest verified Safe source with navigation route |
| `GET`  | `/api/reports` | List community contamination reports |
| `POST` | `/api/reports` | Submit a new citizen water quality report |
| `POST` | `/api/reports/{id}/upvote` | Upvote a community report |
| `GET`  | `/api/alerts` | Active water quality advisory alerts |
| `GET`  | `/api/analytics/summary` | City-wide metrics, stats & safe percentage |

---

## ⚙️ Installation & Setup

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & npm

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/sankalpgaidhane77-star/AquaShield-AI.git
cd AquaShield-AI

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed the database with demo water sources and reports
python backend/seed_data.py

# Start the FastAPI server
uvicorn backend.app.main:app --reload --port 8000
```
Interactive API documentation will be available at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
# In a new terminal, navigate to the frontend folder
cd frontend

# Install npm packages
npm install

# Start the development server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Running Tests

Run the backend test suite:
```bash
pytest backend/tests/
```

Run frontend build verification:
```bash
cd frontend
npm run build
```

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
