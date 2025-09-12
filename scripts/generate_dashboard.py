import os
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, text
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

def main():
    analysis_dir = Path("/opt/airflow/data/analysis")
    analysis_dir.mkdir(parents=True, exist_ok=True)

    df = load_data()
    
    if df is None or df.empty:
        print("No data found in zimmo_data table")
        return False

    print(f"📊 Processing {len(df)} rows of data")
    print(f"Columns available: {df.columns.tolist()}")

    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        initial_count = len(df)
        df = df.dropna(subset=['price'])
        if len(df) < initial_count:
            print(f"Removed {initial_count - len(df)} rows with invalid prices")


    dashboard_data = {
        "summary": {
            "total_properties": len(df),
            "avg_price": float(df['price'].mean()) if 'price' in df.columns and not df['price'].empty else None,
            "property_types": df['type'].value_counts().to_dict() if 'type' in df.columns else {},
            "timestamp": datetime.now().isoformat()
        },
        "price_statistics": {},
        "location_statistics": {},
        "model_prediction": {}
    }


    if 'price' in df.columns and not df['price'].empty:
        try:
            dashboard_data["price_statistics"] = {
                "min": float(df['price'].min()),
                "max": float(df['price'].max()),
                "median": float(df['price'].median()),
                "std": float(df['price'].std()),
                "count": int(df['price'].count())
            }
            print("✅ Added price statistics to dashboard")
        except Exception as e:
            print(f"Error calculating price statistics: {e}")


    if 'city' in df.columns:
        try:
            city_counts = df['city'].value_counts()
            dashboard_data["location_statistics"] = {
                str(city): int(count) for city, count in city_counts.head(20).items()
            }
            print("✅ Added location statistics to dashboard")
        except Exception as e:
            print(f"Error calculating location statistics: {e}")

    model_metrics_file = Path("/opt/airflow/data/models/latest_model_metrics.json")
    if model_metrics_file.exists():
        try:
            with open(model_metrics_file) as f:
                metrics = json.load(f)
                dashboard_data["model_prediction"] = metrics
                print("✅ Loaded model metrics successfully")
        except Exception as e:
            print(f"Could not load model metrics: {e}")

    dashboard_file = analysis_dir / f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(dashboard_file, "w") as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        
    
        latest_file = analysis_dir / "latest_dashboard.json"
        with open(latest_file, "w") as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        
        print(f"✅ Dashboard data generated and saved to {dashboard_file}")
        print(f"✅ Latest dashboard saved to {latest_file}")
        
        print(f"📊 Dashboard Summary:")
        print(f"  - Total properties: {dashboard_data['summary']['total_properties']}")
        if dashboard_data['summary']['avg_price']:
            print(f"  - Average price: €{dashboard_data['summary']['avg_price']:,.2f}")
        if dashboard_data['price_statistics']:
            print(f"  - Price range: €{dashboard_data['price_statistics']['min']:,.0f} - €{dashboard_data['price_statistics']['max']:,.0f}")
        
        return str(dashboard_file)
        
    except Exception as e:
        print(f"Error saving dashboard: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = main()
    if not result:
        sys.exit(1)