import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.preprocessing import StandardScaler
import joblib
import warnings
import psycopg2
from urllib.parse import urlparse

def get_connection_params():
    try:
        from airflow.models import Connection
        conn = Connection.get_connection_from_secrets("postgres_default")
        
        return {
            'host': conn.host,
            'port': conn.port,
            'database': conn.schema,
            'user': conn.login,
            'password': conn.password
        }
    except Exception as e:
        print(f"Error getting Airflow connection: {e}")
        uri = os.getenv("AIRFLOW_CONN_POSTGRES_DEFAULT")
        if not uri:
            raise RuntimeError("AIRFLOW_CONN_POSTGRES_DEFAULT not set")
        
        parsed = urlparse(uri)
        return {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path.lstrip('/'),
            'user': parsed.username,
            'password': parsed.password
        }

def load_data():
    try:
        conn_params = get_connection_params()

        conn_string = f"host='{conn_params['host']}' port='{conn_params['port']}' dbname='{conn_params['database']}' user='{conn_params['user']}' password='{conn_params['password']}'"
        

        conn = psycopg2.connect(conn_string)
        
        df = pd.read_sql("SELECT * FROM zimmo_data", con=conn)
        conn.close()
        
        print(f"Method 2 (psycopg2): Successfully loaded {len(df)} rows")
        return df
        
    except Exception as e:
        print(f"Method 2 (psycopg2) failed: {e}")
        return None
    
def preprocess_data(df):
    """Preprocess data for machine learning"""
    print("Starting data preprocessing...")
    

    print(f"Initial dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    

    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        print(f"Price column converted to numeric")
    

    initial_rows = len(df)
    df = df.dropna(subset=['price'])
    print(f"Removed {initial_rows - len(df)} rows with missing prices")

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    target_col = 'price'
    exclude_cols = ['id', 'zimmo_code', 'url']  
    
    feature_cols = [col for col in numeric_cols 
                   if col != target_col and 
                   not any(exclude in col.lower() for exclude in exclude_cols)]
    
    print(f"Target column: {target_col}")
    print(f"Feature columns: {feature_cols}")
    
    if not feature_cols:
        print("Error: No suitable feature columns found!")
        return None, None, None
    
    if target_col not in df.columns:
        print(f"Error: Target column '{target_col}' not found!")
        return None, None, None
    

    X = df[feature_cols].copy()
    y = df[target_col].copy()
    

    print("Handling missing values...")
    missing_counts = X.isnull().sum()
    if missing_counts.any():
        print("Missing values per column:")
        for col, count in missing_counts[missing_counts > 0].items():
            print(f"  {col}: {count}")
        
       
        X = X.fillna(X.median())
    
    q1 = y.quantile(0.25)
    q3 = y.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    outlier_mask = (y >= lower_bound) & (y <= upper_bound)
    X = X[outlier_mask]
    y = y[outlier_mask]
    
    outliers_removed = len(df) - len(X)
    if outliers_removed > 0:
        print(f"Removed {outliers_removed} outliers")
    
    print(f"Final dataset shape: {X.shape}")
    print(f"Target range: {y.min():,.0f} - {y.max():,.0f}")
    
    return X, y, feature_cols

def train_model(X, y, feature_cols):
    """Train the regression model"""
    print("Starting model training...")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=None
    )
    
    print(f"Training set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestRegressor(
        n_estimators=100,  
        random_state=42,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        n_jobs=-1 
    )
    
    print("Training Random Forest model...")
    model.fit(X_train_scaled, y_train)
    

    y_pred_train = model.predict(X_train_scaled)
    y_pred_test = model.predict(X_test_scaled)
    
    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    
    metrics = {
        "train_mae": float(train_mae),
        "test_mae": float(test_mae),
        "train_r2": float(train_r2),
        "test_r2": float(test_r2),
        "train_rmse": float(train_rmse),
        "test_rmse": float(test_rmse),
        "features_used": feature_cols,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_importance": dict(zip(feature_cols, model.feature_importances_.tolist()))
    }
    
    print(f"✅ Model Training Results:")
    print(f"  Training MAE: €{train_mae:,.2f}")
    print(f"  Test MAE: €{test_mae:,.2f}")
    print(f"  Training R²: {train_r2:.3f}")
    print(f"  Test R²: {test_r2:.3f}")
    print(f"  Training RMSE: €{train_rmse:,.2f}")
    print(f"  Test RMSE: €{test_rmse:,.2f}")
    
    return model, scaler, metrics

def save_model_and_metrics(model, scaler, metrics):
    """Save the trained model and its metrics"""
    base_dir = Path("/opt/airflow/data")
    models_dir = base_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save model
    model_filename = f"price_model_{timestamp}.joblib"
    model_path = models_dir / model_filename
    
    # Save both model and scaler together
    model_data = {
        'model': model,
        'scaler': scaler,
        'timestamp': timestamp,
        'features': metrics['features_used']
    }
    
    joblib.dump(model_data, model_path)
    print(f"✅ Model and scaler saved to {model_path}")
    
    # Save metrics
    metrics_data = {
        "model_file": model_filename,
        "timestamp": timestamp,
        **metrics
    }
    
    metrics_file = models_dir / "latest_model_metrics.json"
    try:
        with open(metrics_file, "w") as f:
            json.dump(metrics_data, f, indent=2)
        print(f"📊 Metrics saved to {metrics_file}")
    except Exception as e:
        print(f"Failed to save metrics: {e}")
    
    return str(model_path)

def main():
    print("🚀 Starting ML model training pipeline...")
    
    try:
        df = load_data()
        if df is None or df.empty:
            print("❌ No data available for training")
            return False
        
        X, y, feature_cols = preprocess_data(df)
        if X is None:
            print("❌ Data preprocessing failed")
            return False
        
        if len(X) < 10:
            print("❌ Insufficient data for training (need at least 10 samples)")
            return False

        model, scaler, metrics = train_model(X, y, feature_cols)
        
        model_path = save_model_and_metrics(model, scaler, metrics)
        
        print(f"🎉 Training pipeline completed successfully!")
        print(f"📁 Model saved to: {model_path}")
        
        return model_path
        
    except Exception as e:
        print(f"❌ Training pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = main()
    if not result:
        sys.exit(1) 