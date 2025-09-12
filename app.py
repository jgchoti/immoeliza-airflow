import streamlit as st
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


st.set_page_config(
    page_title="Immo-Eliza Dashboard", 
    layout="wide",
    page_icon="🏠"
)

DATA_DIR = Path("data/analysis")
MODEL_DIR = Path("data/models")
LATEST_FILE = DATA_DIR / "latest_dashboard.json"
LATEST_FILE_MODEL = MODEL_DIR/ "latest_model_metrics.json"


@st.cache_data(ttl=300)  
def load_data(type_data = "data"):
    
    file = LATEST_FILE
    dir_file = DATA_DIR
    file_name = "dashboard_*.json"
    if type_data is "model":
        file = LATEST_FILE_MODEL
        dir_file = MODEL_DIR
        file_name = "price_model_*.json"
  
    if file.exists():
        with open(file, "r") as f:
            return json.load(f)
    else:
        json_files = sorted(dir_file.glob(file_name), reverse=True)
        if json_files:
            with open(json_files[0], "r") as f:
                return json.load(f)
        return None
    
dashboard_data = load_data("data")

if not dashboard_data:
    st.error("❌ No dashboard data found.")
    st.stop()


st.title("🏠 Immo-Eliza Real Estate Dashboard")


summary = dashboard_data.get("summary", {})
timestamp = summary.get("timestamp", "Unknown")
if timestamp != "Unknown":
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        st.caption(f"Last updated: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    except:
        st.caption(f"Last updated: {timestamp}")


if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()


col1, col2, col3, col4 = st.columns(4)

with col1:
    total_props = summary.get("total_properties", 0)
    st.metric("📊 Total Properties", f"{total_props:,}")

with col2:
    avg_price = summary.get("avg_price")
    if avg_price:
        st.metric("💰 Average Price", f"€{avg_price:,.0f}")
    else:
        st.metric("💰 Average Price", "N/A")

with col3:
    price_stats = dashboard_data.get("price_statistics", {})
    if price_stats.get("min") and price_stats.get("max"):
        price_range = f"€{price_stats['min']:,.0f} - €{price_stats['max']:,.0f}"
        st.metric("📈 Price Range", price_range)
    else:
        st.metric("📈 Price Range", "N/A")

with col4:
    model_data = load_data("model")
    if model_data.get("test_r2"):
        r2_score = model_data["test_r2"]
        st.metric("🎯 Model R² Score", f"{r2_score:.3f}")
    else:
        st.metric("🎯 Model R² Score", "N/A")

st.divider()

tabs = st.tabs(["🏘️ Property Overview", "💰 Price Analysis", "📍 Location Insights", "🤖 Model Performance"])


with tabs[0]:
    st.header("Property Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Property Types Distribution")
        property_types = summary.get("property_types", {})
        if property_types:
            df_types = pd.DataFrame.from_dict(property_types, orient="index", columns=["Count"])
            df_types = df_types.sort_values("Count", ascending=False)

            fig = px.pie(
                values=df_types["Count"], 
                names=df_types.index,
                title="Properties by Type"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No property type data available")
    
    with col2:
        st.subheader("Key Statistics")
        if price_stats:
            stats_data = {
                "Metric": ["Count", "Minimum Price", "Maximum Price", "Median Price", "Standard Deviation"],
                "Value": [
                    f"{price_stats.get('count', 'N/A'):,}",
                    f"€{price_stats.get('min', 0):,.0f}",
                    f"€{price_stats.get('max', 0):,.0f}",
                    f"€{price_stats.get('median', 0):,.0f}",
                    f"€{price_stats.get('std', 0):,.0f}"
                ]
            }
            st.dataframe(pd.DataFrame(stats_data), hide_index=True, use_container_width=True)


with tabs[1]:
    st.header("Price Analysis")
    
    if price_stats:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Price Distribution Metrics")
            
            fig = go.Figure()
            fig.add_trace(go.Box(
                q1=[price_stats.get('min', 0)],
                median=[price_stats.get('median', 0)],
                q3=[price_stats.get('max', 0)],
                mean=[summary.get('avg_price', 0)],
                name="Price Distribution",
                boxmean=True
            ))
            fig.update_layout(title="Price Distribution Overview")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Price Metrics")
            metrics_df = pd.DataFrame({
                "Metric": ["Minimum", "25th Percentile", "Median (50th)", "Mean (Average)", "75th Percentile", "Maximum", "Standard Deviation"],
                "Price (€)": [
                    f"{price_stats.get('min', 0):,.0f}",
                    "N/A", 
                    f"{price_stats.get('median', 0):,.0f}",
                    f"{summary.get('avg_price', 0):,.0f}",
                    "N/A",  
                    f"{price_stats.get('max', 0):,.0f}",
                    f"{price_stats.get('std', 0):,.0f}"
                ]
            })
            st.dataframe(metrics_df, hide_index=True, use_container_width=True)
    else:
        st.info("No price statistics available")

with tabs[2]:
    st.header("Location Insights")
    
    location_stats = dashboard_data.get("location_statistics", {})
    if location_stats:
        location_df = pd.DataFrame.from_dict(location_stats, orient="index", columns=["Count"])
        location_df = location_df.sort_values("Count", ascending=False).head(20)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Cities by Property Count")
            fig = px.bar(
                x=location_df["Count"], 
                y=location_df.index,
                orientation='h',
                title="Properties per City (Top 20)"
            )
            fig.update_layout(yaxis_title="City", xaxis_title="Number of Properties")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("City Statistics")
            location_df_display = location_df.copy()
            location_df_display.index.name = "City"
            location_df_display["Percentage"] = (location_df_display["Count"] / location_df_display["Count"].sum() * 100).round(1)
            st.dataframe(location_df_display, use_container_width=True)
            
            st.metric("Total Cities", len(location_stats))
    else:
        st.info("No location data available")


with tabs[3]:
    st.header("Model Performance")
    
    if model_data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Model Metrics")
            
            metrics = {
                "Metric": ["Training R² Score", "Test R² Score", "Training MAE", "Test MAE", "Training RMSE", "Test RMSE"],
                "Value": [
                    f"{model_data.get('train_r2', 'N/A'):.3f}" if model_data.get('train_r2') else "N/A",
                    f"{model_data.get('test_r2', 'N/A'):.3f}" if model_data.get('test_r2') else "N/A",
                    f"€{model_data.get('train_mae', 0):,.0f}" if model_data.get('train_mae') else "N/A",
                    f"€{model_data.get('test_mae', 0):,.0f}" if model_data.get('test_mae') else "N/A",
                    f"€{model_data.get('train_rmse', 0):,.0f}" if model_data.get('train_rmse') else "N/A",
                    f"€{model_data.get('test_rmse', 0):,.0f}" if model_data.get('test_rmse') else "N/A"
                ]
            }
            
            metrics_df = pd.DataFrame(metrics)
            st.dataframe(metrics_df, hide_index=True, use_container_width=True)
        
        with col2:
            st.subheader("Training Information")
            
            training_info = {
                "Info": ["Model File", "Training Samples", "Test Samples", "Features Used", "Timestamp"],
                "Value": [
                    model_data.get("model_file", "N/A"),
                    f"{model_data.get('training_samples', 0):,}",
                    f"{model_data.get('test_samples', 0):,}",
                    len(model_data.get('features_used', [])),
                    model_data.get('timestamp', 'N/A')
                ]
            }
            
            info_df = pd.DataFrame(training_info)
            st.dataframe(info_df, hide_index=True, use_container_width=True)
        
        if model_data.get('feature_importance'):
            st.subheader("Feature Importance")
            
            feature_importance = model_data['feature_importance']
            importance_df = pd.DataFrame.from_dict(feature_importance, orient="index", columns=["Importance"])
            importance_df = importance_df.sort_values("Importance", ascending=True).tail(10)  # Top 10 features
            
            fig = px.bar(
                x=importance_df["Importance"], 
                y=importance_df.index,
                orientation='h',
                title="Top 10 Most Important Features"
            )
            fig.update_layout(yaxis_title="Feature", xaxis_title="Importance Score")
            st.plotly_chart(fig, use_container_width=True)
        

        if model_data.get('test_r2') and model_data.get('test_mae'):
            st.subheader("Model Performance Summary")
            r2 = model_data['test_r2']
            mae = model_data['test_mae']
            
            if r2 > 0.8:
                performance = "Excellent"
                color = "green"
            elif r2 > 0.6:
                performance = "Good"
                color = "orange"
            else:
                performance = "Needs Improvement"
                color = "red"
            
            st.markdown(f"**Model Performance: <span style='color:{color}'>{performance}</span>**", unsafe_allow_html=True)
            st.write(f"- The model explains {r2*100:.1f}% of price variance")
            st.write(f"- Average prediction error: €{mae:,.0f}")
    else:
        st.info("No model performance data available. Please run the model training task first.")


st.divider()
st.caption("📊 Immo-Eliza Dashboard | Powered by Airflow Pipeline | Data updates automatically every pipeline run")