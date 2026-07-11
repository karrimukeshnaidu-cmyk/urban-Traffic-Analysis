# TrafficWise AI 🚦 — Urban Traffic Analytics & Prediction System

TrafficWise AI is an industry-grade, full-stack data analytics and predictive forecasting application built using **Flask (Python)**, **MySQL**, and **Chart.js**. It features a robust machine learning backend (powered by **XGBoost**) to forecast future traffic volumes, identify peak congestion windows, and categorize traffic levels (Low, Medium, High). 

The frontend showcases a responsive dashboard equipped with 7 interactive charts, Light/Dark mode toggles, loading skeletons, modal overlays, and a live prediction panel.

---

## 🌟 Key Features

* **Advanced Predictive Modeling**: Powered by an optimized **XGBoost Regressor** trained on historical records, achieving high R-squared accuracy ($R^2 = 0.679$).
* **Live 24-Hour Peak Simulation**: The API runs real-time inference for a full 24-hour block of any given location and target date to forecast and locate the exact peak congestion hour.
* **SQL Injection Protection**: Fully parameterized query execution across all database interactions.
* **Database Connection Pooling**: Caches database connections to support high-throughput, multi-threaded request processing.
* **Dynamic Charting & Interactive Fullscreen**: 7 responsive Chart.js visual graphs that instantly re-render style parameters (labels, gridlines, colors) upon theme change, supporting overlays.
* **Light/Dark Mode Toggling**: Sleek glassmorphic aesthetics that persist themes across sessions using local storage.

---

## 🛠️ Technology Stack

* **Backend**: Flask (Python 3.11+)
* **Database**: MySQL (Connection pooling, parameterized raw queries)
* **Machine Learning**: Pandas, NumPy, Scikit-Learn, XGBoost, Joblib
* **Frontend**: HTML5, CSS3 (variables & transitions), JS, Chart.js

---

## 📂 Directory Layout

```
├── app.py                      # Central entry point registering blueprints
├── train_model.py              # ML pipeline training and comparison script
├── requirements.txt            # Python dependencies lists
├── Dockerfile                  # Container config for deployment
├── Procfile                    # Web execution command for PaaS platforms
├── .gitignore                  # Git commit exclusions
├── .dockerignore               # Docker build exclusions
├── models/
│   ├── db.py                   # Parameterized DB connection pool manager
│   └── traffic_model.pkl       # Saved XGBoost pipeline (preprocessor + model)
├── routes/
│   ├── dashboard.py            # Renders core dashboard UI and pulls stats
│   └── api.py                  # Handles prediction and query data JSON API
├── templates/
│   └── index.html              # Modern glassmorphism HTML layout
└── static/
    ├── css/
    │   └── style.css           # Themeable CSS (supports Light & Dark themes)
    └── js/
        └── script.js           # Theme listener, Chart.js setup, prediction fetcher
```

---

## 🚀 Getting Started (Local Run)

### 1. Database Configuration
1. Initialize your MySQL server and create a database named `traffic_db`:
   ```sql
   CREATE DATABASE traffic_db;
   ```
2. Create the `traffic_data` table and populate it with historical records. Ensure your MySQL credentials are set in [models/db.py](models/db.py) and [train_model.py](train_model.py):
   ```python
   db_config = {
       "host": "localhost",
       "user": "root",
       "password": "your_password",
       "database": "traffic_db"
   }
   ```

### 2. Environment Setup & Dependency Installation
Create a virtual environment and install the required modules:
```bash
# Create venv
python -m venv venv

# Activate venv (Windows)
.\venv\Scripts\activate
# Activate venv (Linux/macOS)
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Model Training & Serialization
To train and compile the machine learning pipeline, execute the training script:
```bash
python train_model.py
```
*This script will fetch historical data, evaluate multiple model candidates (Linear Regression, Random Forest, XGBoost), log evaluation metrics (MAE, RMSE, $R^2$), and serialize the best pipeline to `models/traffic_model.pkl`.*

### 4. Running the Web App
Start the Flask development server:
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 🔮 API Endpoints

### 1. GET/POST `/predict`
Retrieves vehicle density predictions and daily peak congestion analytics.

* **Query Parameters / JSON Payload**:
  * `location` (integer): Junction ID (`1`, `2`, `3`, or `4`).
  * `date` (string): Target date (`YYYY-MM-DD`).
  * `hour` (integer): Target hour (`0`-`23`).

* **Example JSON Response**:
  ```json
  {
    "status": "success",
    "data": {
      "location": 1,
      "date": "2026-07-12",
      "day_name": "Sunday",
      "hour": 12,
      "predicted_traffic": 35.94,
      "predicted_vehicles": 36,
      "traffic_category": "High",
      "peak_hour": 22,
      "peak_hour_formatted": "22:00",
      "peak_volume": 43.57,
      "hourly_predictions": [36.0, 31.3, 24.9, 22.6, 21.2, 18.9, 19.5, 22.5, 25.1, 28.2, 32.5, 35.2, 35.9, 33.9, 32.2, 33.1, 32.8, 35.5, 40.9, 42.8, 42.5, 42.1, 43.6, 40.2]
    }
  }
  ```

---

## 🐳 Deployment Guide

### Option A: Deploying via Docker
1. **Build the Docker Image**:
   ```bash
   docker build -t trafficwise-ai .
   ```
2. **Run the Container**:
   ```bash
   docker run -p 5000:5000 --env PORT=5000 -d trafficwise-ai
   ```

### Option B: Deploying to Render
1. Create a new **Web Service** on Render and link this GitHub repository.
2. Select **Python 3** environment (or choose **Docker** to deploy with the Dockerfile automatically).
3. Build & Start Commands (if not deploying via Docker):
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `gunicorn app:app`
4. Set Environment Variables:
   * Define your MySQL database URL connection variables (using database integrations like Aiven or AWS RDS for production).
