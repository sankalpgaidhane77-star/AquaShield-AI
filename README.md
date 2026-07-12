<div align="center">
  <img src="https://img.shields.io/badge/Water-Security-00B4D8?style=for-the-badge&logo=water&logoColor=white" alt="Water Security" />
  <img src="https://img.shields.io/badge/AI-Powered-FF6B35?style=for-the-badge&logo=artificial-intelligence&logoColor=white" alt="AI Powered" />
  <img src="https://img.shields.io/badge/Real--Time-Monitoring-2E8B57?style=for-the-badge&logo=grafana&logoColor=white" alt="Real-Time Monitoring" />
</div>

<br/>

<div align="center">
  <h1>🌊 AquaShield AI</h1>
  <p><strong>Intelligent Water Quality Monitoring & Prediction Platform</strong></p>
  
  [![React](https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB)](https://reactjs.org/)
  [![Node.js](https://img.shields.io/badge/Node.js-43853D?style=flat-square&logo=node.js&logoColor=white)](https://nodejs.org/)
  [![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
  [![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
  [![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

</div>

---

## 📖 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [API Endpoints](#-api-endpoints)
- [ML Model](#-ml-model)
- [Installation & Setup](#-installation--setup)
- [Usage Guide](#-usage-guide)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🎯 Overview

**AquaShield AI** is a comprehensive water security platform that leverages machine learning to predict water quality and provide real-time monitoring solutions. Built with a modern full-stack architecture, it offers community-driven reporting, location-based services, and intelligent safety classification to ensure access to safe drinking water.

### 🚀 Why AquaShield AI?
- **Early Warning System**: Predicts water quality issues before they become critical
- **Community-Driven**: Empowers citizens to report and track water contamination
- **Accessible Insights**: Provides actionable recommendations for water safety
- **Scalable Architecture**: Designed for expansion to smart city infrastructure

---

## ✨ Key Features

### 🏠 **Home Dashboard**
- Platform overview with quick navigation
- Real-time water quality statistics
- Interactive call-to-action buttons

### 📊 **Live Monitoring**
- **Real-time Metrics**: pH, Turbidity, TDS, Temperature with simulated drift
- **7-Day Trend Analysis**: Historical data visualization with interactive charts
- **Instant Alerts**: Visual indicators for parameter thresholds

### 🤖 **AI Prediction Engine**
- **Input Parameters**: pH, Turbidity, TDS, Temperature
- **Safety Classification**: 
  - 🟢 Safe (Green)
  - 🟡 Moderate (Yellow) 
  - 🔴 Dangerous (Red)
- **Confidence Scoring**: Probability-based classification
- **Actionable Recommendations**: Customized suggestions based on results

### 🗺️ **Water Locator**
- **Interactive Map**: Find nearby safe water sources
- **Location Types**:
  - Springs & Natural Sources
  - Purification Wells
  - Public Tap Stations
  - Accredited Testing Facilities
- **Quality Metrics**: Status and parameter data for each location

### 🚨 **Issue Reporting**
- **Community Reporting**: Submit contamination reports
- **Categories**: Industrial Runoff, Algal Bloom, Sewage, Chemical Spill
- **GPS Integration**: Automatic location tagging
- **Photo Upload**: Visual evidence submission
- **Status Tracking**: Reported → Investigating → Resolved

---

## 💻 Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI Framework |
| **Vite** | Build Tool |
| **TailwindCSS** | Styling |
| **React Router DOM** | Navigation |
| **Recharts** | Data Visualization |
| **Leaflet** | Interactive Maps |
| **Axios** | API Communication |

### Backend
| Technology | Purpose |
|------------|---------|
| **Node.js** | Runtime Environment |
| **Express.js** | Web Framework |
| **CORS** | Cross-Origin Resource Sharing |
| **Dotenv** | Environment Variables |

### Machine Learning
| Technology | Purpose |
|------------|---------|
| **Flask** | ML Service API |
| **Python 3.9+** | Core Language |
| **NumPy** | Numerical Computing |
| **Custom RF** | 5-Tree Random Forest Implementation |

---

## 🔌 API Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `GET` | `/api/metrics` | Live + historical water data | - |
| `GET` | `/api/locations` | Safe sources & testing facilities | - |
| `GET` | `/api/issues` | All reported contamination issues | - |
| `POST` | `/api/issues` | Submit a new issue report | `{ category, description, lat, lng, photo }` |
| `POST` | `/api/predict` | AI water quality prediction | `{ ph, turbidity, tds, temperature }` |

