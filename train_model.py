import os
import pickle
import pandas as pd
import numpy as np
import mysql.connector
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from models.db import db_config

def load_data_from_db():
    print("Connecting to MySQL Database...")
    conn = mysql.connector.connect(**db_config)
    
    # Query database
    query = "SELECT timestamp, location, vehicle_count FROM traffic_data"
    print("Reading data from traffic_data table...")
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"Successfully loaded {len(df)} records.")
    return df

def preprocess_and_engineer_features(df):
    print("Performing feature engineering...")
    df = df.copy()
    
    # Convert to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Extract features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.weekday  # 0: Monday, 6: Sunday
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Prepare features and target
    X = df[['location', 'hour', 'day_of_week', 'is_weekend']]
    y = df['vehicle_count']
    
    return X, y

def train_and_evaluate():
    # 1. Load data
    df = load_data_from_db()
    
    # 2. Preprocess & Feature Engineering
    X, y = preprocess_and_engineer_features(df)
    
    # 3. Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=True)
    
    # Define Column Transformer for One-Hot Encoding location
    # Since locations are categorical IDs [1, 2, 3, 4]
    preprocessor = ColumnTransformer(
        transformers=[
            ('loc', OneHotEncoder(categories=[[1, 2, 3, 4]], handle_unknown='ignore', sparse_output=False), ['location'])
        ],
        remainder='passthrough'
    )
    
    # List of models to evaluate
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    }
    
    # Try importing XGBoost if installed
    try:
        from xgboost import XGBRegressor
        models['XGBoost'] = XGBRegressor(n_estimators=150, max_depth=7, learning_rate=0.1, random_state=42, n_jobs=-1)
        print("XGBoost is available and will be evaluated.")
    except ImportError:
        print("XGBoost is not installed or available. Continuing with Linear Regression and Random Forest.")
        
    results = {}
    best_rmse = float('inf')
    best_model_name = None
    best_pipeline = None
    
    print("\nStarting model evaluation...")
    for name, model in models.items():
        print(f"Training {name}...")
        
        # Build pipeline
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', model)
        ])
        
        # Train
        pipeline.fit(X_train, y_train)
        
        # Predict
        y_train_pred = pipeline.predict(X_train)
        y_test_pred = pipeline.predict(X_test)
        
        # Metrics
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        
        results[name] = {
            'Train MAE': train_mae,
            'Test MAE': test_mae,
            'Train RMSE': train_rmse,
            'Test RMSE': test_rmse,
            'Train R2': train_r2,
            'Test R2': test_r2,
            'pipeline': pipeline
        }
        
        print(f"{name} - Test MAE: {test_mae:.4f}, Test RMSE: {test_rmse:.4f}, Test R2: {test_r2:.4f}")
        
        if test_rmse < best_rmse:
            best_rmse = test_rmse
            best_model_name = name
            best_pipeline = pipeline
            
    # Print Comparison Table
    print("\n" + "="*80)
    print(f"{'Model Name':<20} | {'Test MAE':<12} | {'Test RMSE':<12} | {'Test R2':<12}")
    print("="*80)
    for name, metrics in results.items():
        print(f"{name:<20} | {metrics['Test MAE']:<12.4f} | {metrics['Test RMSE']:<12.4f} | {metrics['Test R2']:<12.4f}")
    print("="*80)
    
    print(f"\nBest Model: {best_model_name} (Test RMSE: {best_rmse:.4f})")
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Save the best model
    model_path = os.path.join('models', 'traffic_model.pkl')
    print(f"Saving best model pipeline to {model_path}...")
    with open(model_path, 'wb') as f:
        pickle.dump(best_pipeline, f)
        
    print("Model pipeline saved successfully!")

if __name__ == '__main__':
    train_and_evaluate()
