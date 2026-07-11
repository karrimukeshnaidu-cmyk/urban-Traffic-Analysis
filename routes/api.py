import os
import pickle
from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np
from models.db import get_db_connection

api_bp = Blueprint('api', __name__)

# Global model cache
_model = None

def get_model():
    """
    Lazy loads the machine learning model pipeline.
    """
    global _model
    if _model is None:
        model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'traffic_model.pkl')
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                _model = pickle.load(f)
        else:
            raise FileNotFoundError("Trained model file not found at models/traffic_model.pkl. Please run train_model.py first.")
    return _model

@api_bp.route('/predict', methods=['GET', 'POST'])
def predict():
    try:
        # Get parameters from request (support both JSON POST and URL Query GET)
        if request.method == 'POST':
            data = request.get_json() or {}
            location = data.get('location')
            date_str = data.get('date')
            hour = data.get('hour')
        else:
            location = request.args.get('location')
            date_str = request.args.get('date')
            hour = request.args.get('hour')

        # Validation
        if location is None or date_str is None or hour is None:
            return jsonify({
                "status": "error",
                "message": "Missing parameters. Required: 'location', 'date', and 'hour'."
            }), 400

        try:
            location = int(location)
            hour = int(hour)
            if not (0 <= hour <= 23):
                raise ValueError("Hour must be between 0 and 23.")
            if location not in [1, 2, 3, 4]:
                raise ValueError("Location must be 1, 2, 3, or 4.")
        except ValueError as ve:
            return jsonify({"status": "error", "message": f"Invalid input format: {str(ve)}"}), 400

        # Parse date and extract day_of_week and weekend flag
        try:
            parsed_date = pd.to_datetime(date_str)
            day_of_week = parsed_date.weekday()  # 0: Monday, 6: Sunday
            is_weekend = 1 if day_of_week in [5, 6] else 0
            day_name = parsed_date.day_name()
        except Exception as e:
            return jsonify({"status": "error", "message": f"Invalid date format: {str(e)}"}), 400

        # Load model
        model = get_model()

        # Build feature DataFrame for the target prediction
        target_df = pd.DataFrame([{
            'location': location,
            'hour': hour,
            'day_of_week': day_of_week,
            'is_weekend': is_weekend
        }])

        # Run prediction
        prediction = model.predict(target_df)[0]
        prediction_val = max(0.0, float(prediction))  # Traffic cannot be negative

        # Classify traffic category
        # Thresholds: Low <= 15, Medium 15-30, High > 30
        if prediction_val <= 15.0:
            category = "Low"
        elif prediction_val <= 30.0:
            category = "Medium"
        else:
            category = "High"

        # Predict all 24 hours of that day to find the peak congestion hour
        hours_df = pd.DataFrame([{
            'location': location,
            'hour': h,
            'day_of_week': day_of_week,
            'is_weekend': is_weekend
        } for h in range(24)])

        all_day_predictions = model.predict(hours_df)
        all_day_predictions = np.maximum(0.0, all_day_predictions)
        
        peak_hour = int(np.argmax(all_day_predictions))
        peak_volume = float(all_day_predictions[peak_hour])

        # Return full prediction package
        return jsonify({
            "status": "success",
            "data": {
                "location": location,
                "date": date_str,
                "day_name": day_name,
                "hour": hour,
                "predicted_traffic": round(prediction_val, 2),
                "predicted_vehicles": int(round(prediction_val)),
                "traffic_category": category,
                "peak_hour": peak_hour,
                "peak_hour_formatted": f"{peak_hour:02d}:00",
                "peak_volume": round(peak_volume, 2),
                "hourly_predictions": [round(float(p), 1) for p in all_day_predictions]
            }
        })

    except FileNotFoundError as fnf:
        return jsonify({"status": "error", "message": str(fnf)}), 503
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

@api_bp.route('/api/data', methods=['GET'])
def get_historical_data():
    """
    Returns filtered historical data as JSON (for async front-end loading).
    """
    selected_day = request.args.get('day')
    selected_location = request.args.get('location')

    filter_query = "WHERE 1=1"
    params = []

    if selected_day:
        filter_query += " AND day = %s"
        params.append(selected_day)

    if selected_location:
        try:
            filter_query += " AND location = %s"
            params.append(int(selected_location))
        except ValueError:
            pass

    conn = get_db_connection()
    try:
        query = f"SELECT timestamp, location, vehicle_count, hour, day FROM traffic_data {filter_query} LIMIT 100"
        df = pd.read_sql(query, conn, params=params)
        df['timestamp'] = df['timestamp'].astype(str)
        data = df.to_dict(orient='records')
        return jsonify({
            "status": "success",
            "count": len(data),
            "data": data
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()
