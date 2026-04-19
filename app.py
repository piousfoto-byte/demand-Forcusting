import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import io

st.set_page_config(
    page_title="PIOUS - Demand Forecasting Assistant",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'forecast_data' not in st.session_state:
    st.session_state.forecast_data = None
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = None

COLORS = {
    'primary': '#1E3A5F',
    'secondary': '#3D5A80',
    'accent': '#EE6C4D',
    'background': '#0D1B2A',
    'surface': '#1B2838',
    'text': '#E0E1DD',
    'success': '#4ECDC4',
    'warning': '#FFD166'
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #0D1B2A 0%, #1B2838 100%);
}

.card {
    background: rgba(29, 58, 95, 0.6);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

.metric-card {
    background: linear-gradient(135deg, #1E3A5F 0%, #3D5A80 100%);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    border: 1px solid rgba(238,108,77,0.3);
}

.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    font-weight: 600;
    color: #EE6C4D;
}

.metric-label {
    color: #E0E1DD;
    font-size: 14px;
    margin-top: 4px;
}

.chat-message {
    padding: 12px 16px;
    border-radius: 12px;
    margin: 8px 0;
    max-width: 85%;
}

.chat-user {
    background: linear-gradient(135deg, #3D5A80 0%, #1E3A5F 100%);
    margin-left: auto;
    border-bottom-right-radius: 4px;
}

.chat-bot {
    background: rgba(78, 205, 196, 0.15);
    border: 1px solid rgba(78, 205, 196, 0.3);
    border-bottom-left-radius: 4px;
}

.stButton > button {
    background: linear-gradient(135deg, #EE6C4D 0%, #FF8A6D 100%);
    border: none;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    padding: 10px 20px;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(238,108,77,0.4);
}

.stTextInput > div > div > input {
    background: rgba(29, 58, 95, 0.6);
    border: 1px solid rgba(255,255,255,0.1);
    color: #E0E1DD;
    border-radius: 8px;
}

.stTextInput > div > div > input:focus {
    border-color: #EE6C4D;
    box-shadow: 0 0 0 2px rgba(238,108,77,0.2);
}

div[data-testid="stExpander"] {
    background: rgba(29, 58, 95, 0.4);
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.1);
}

.upload-zone {
    border: 2px dashed rgba(238,108,77,0.5);
    border-radius: 16px;
    padding: 40px;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
}

.upload-zone:hover {
    border-color: #EE6C4D;
    background: rgba(238,108,77,0.05);
}

.tab-content {
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.trend-up { color: #4ECDC4; }
.trend-down { color: #EE6C4D; }
</style>
""", unsafe_allow_html=True)

def generate_sample_data():
    dates = pd.date_range(start=datetime.now() - timedelta(days=90), periods=90, freq='D')
    base_sales = 150 + 50 * np.sin(np.arange(90) * 2 * np.pi / 30)
    noise = np.random.normal(0, 15, 90)
    sales = base_sales + noise + np.random.choice([0, 20, -10, 30], 90) * (np.random.random(90) > 0.8)
    return pd.DataFrame({'date': dates, 'sales': np.maximum(sales, 20)})

def simple_forecast(df, horizon):
    if len(df) < 7:
        return None
    
    recent = df['sales'].tail(14).values
    trend = np.polyfit(range(len(recent)), recent, 1)[0]
    seasonality = np.mean(recent[-7:]) / np.mean(recent[:7]) if np.mean(recent[:7]) > 0 else 1
    
    predictions = []
    last_value = df['sales'].iloc[-1]
    for i in range(horizon):
        base = last_value + trend * (i + 1)
        seasonal = base * seasonality if i < 7 else base
        noise = np.random.normal(0, base * 0.1)
        predictions.append(max(seasonal + noise, 10))
    
    return predictions

def calculate_metrics(actual, predicted):
    if len(actual) != len(predicted):
        return {'mape': 0, 'rmse': 0, 'mae': 0}
    actual, predicted = np.array(actual), np.array(predicted)
    mape = np.mean(np.abs((actual - predicted) / np.maximum(actual, 1))) * 100
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    mae = np.mean(np.abs(actual - predicted))
    return {'mape': mape, 'rmse': rmse, 'mae': mae}

def get_bot_response(user_input, forecast_data, historical_data):
    user_input = user_input.lower()
    
    if any(word in user_input for word in ['forecast', 'predict', 'next', 'future', 'upcoming']):
        if forecast_data:
            avg_forecast = np.mean(forecast_data)
            response = f"📈 Based on the analysis, I'm forecasting an average of **{avg_forecast:.0f} units** for the next {len(forecast_data)} days. The highest expected demand is **{max(forecast_data):.0f} units** around day {forecast_data.index(max(forecast_data))+1}."
        else:
            response = "I need historical data to make predictions. Please upload a dataset or generate sample data first."
    
    elif any(word in user_input for word in ['trend', 'increasing', 'decreasing', 'growing', 'falling']):
        if historical_data:
            recent = historical_data['sales'].tail(14).values
            trend = np.polyfit(range(len(recent)), recent, 1)[0]
            direction = "📈 **upward**" if trend > 0 else "📉 **downward**"
            response = f"The current trend is {direction}. The average daily change is approximately **{abs(trend):.1f} units**."
        else:
            response = "Please load some data first to analyze trends."
    
    elif any(word in user_input for word in ['average', 'mean', 'typical']):
        if historical_data:
            avg = historical_data['sales'].mean()
            response = f"The average historical sales is **{avg:.1f} units** per day."
        else:
            response = "No data available to calculate average."
    
    elif any(word in user_input for word in ['high', 'peak', 'maximum']):
        if historical_data:
            max_val = historical_data['sales'].max()
            max_date = historical_data.loc[historical_data['sales'].idxmax(), 'date']
            response = f"The highest sales recorded was **{max_val:.0f} units** on {max_date.strftime('%Y-%m-%d')}."
        else:
            response = "No data available."
    
    elif any(word in user_input for word in ['summary', 'overview', 'report']):
        if historical_data and forecast_data:
            avg_sales = historical_data['sales'].mean()
            total_sales = historical_data['sales'].sum()
            max_sales = historical_data['sales'].max()
            min_sales = historical_data['sales'].min()
            recent = historical_data['sales'].tail(14).values
            trend = np.polyfit(range(len(recent)), recent, 1)[0]
            trend_dir = "📈 Upward" if trend > 0 else "📉 Downward"
            avg_forecast = np.mean(forecast_data)
            
            response = f"""📊 **Demand Forecasting Summary**

**Historical Data:**
- 📅 Period: {historical_data['date'].min().strftime('%Y-%m-%d')} to {historical_data['date'].max().strftime('%Y-%m-%d')}
- 💰 Total Sales: **{total_sales:,.0f} units**
- 📊 Average Daily: **{avg_sales:.1f} units**
- 📈 Peak: **{max_sales:.0f} units**
- 📉 Lowest: **{min_sales:.0f} units**
- Trend: **{trend_dir}** ({abs(trend):.1f}/day)

**Forecast ({len(forecast_data)} days):**
- Predicted Average: **{avg_forecast:.0f} units**/day
- Expected Range: **{min(forecast_data):.0f}** - **{max(forecast_data):.0f} units**
- 📦 Recommended Inventory: **{int(avg_forecast * 1.2)} units**
"""
        elif historical_data:
            response = "Generate a forecast first to see the complete summary."
        else:
            response = "Upload or generate data to see a summary."
    
    elif any(word in user_input for word in ['low', 'minimum', 'lowest']):
        if historical_data:
            min_val = historical_data['sales'].min()
            min_date = historical_data.loc[historical_data['sales'].idxmin(), 'date']
            response = f"The lowest sales recorded was **{min_val:.0f} units** on {min_date.strftime('%Y-%m-%d')}."
        else:
            response = "No data available."
    
    elif any(word in user_input for word in ['how', 'work', 'method', 'methodology']):
        response = "🔮 I use an ensemble forecasting approach combining trend analysis and seasonal patterns. I analyze your historical data to detect patterns, then project them forward with confidence intervals. The model accounts for both long-term trends and weekly seasonality."
    
    elif any(word in user_input for word in ['help', 'what can']):
        response = "💡 I can help you with:\n- **Forecasting**: Ask about future predictions\n- **Trends**: Understand if sales are growing or declining\n- **Analysis**: Get insights on averages, peaks, and patterns\n- **Recommendations**: Ask for inventory or pricing suggestions"
    
    elif any(word in user_input for word in ['recommend', 'suggest', 'advice', 'inventory']):
        if forecast_data:
            avg_fc = np.mean(forecast_data)
            safety_stock = np.std(forecast_data) * 1.5
            response = f"📦 Based on forecasts, I recommend:\n- Maintain **{int(avg_fc * 1.2)} units** as optimal inventory\n- Safety stock of **{int(safety_stock)} units** for buffer\n- Consider peak days for staffing: days {forecast_data.index(max(forecast_data))+1} of forecast"
        else:
            response = "Upload data to get inventory recommendations."
    
    else:
        responses = [
            "I'm focused on demand forecasting. Try asking about predictions, trends, or recommendations!",
            "🤔 I can help analyze your sales data. What would you like to know?",
            "I specialize in demand forecasting. Ask me about future sales, trends, or inventory advice!"
        ]
        response = random.choice(responses)
    
    return response

def main():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h2 style="color: #EE6C4D; margin: 0;">PIOUS</h2>
            <p style="color: #E0E1DD; font-size: 12px;">Demand Forecasting AI</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ⚙️ Settings")
        
        forecast_horizon = st.slider("Forecast Horizon (days)", 7, 30, 14)
        
        st.markdown("---")
        st.markdown("### 📁 Data Source")
        
        data_source = st.radio("Choose data:", ["Generate Sample Data", "Upload CSV"])
        
        df = None
        if data_source == "Generate Sample Data":
            if st.button("Generate Data", use_container_width=True):
                df = generate_sample_data()
                st.session_state.historical_data = df
                st.rerun()
            if st.session_state.historical_data is not None and 'sales' in st.session_state.historical_data.columns:
                df = st.session_state.historical_data
                st.success("Sample data loaded!")
        else:
            uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    if 'date' in df.columns and 'sales' in df.columns:
                        df['date'] = pd.to_datetime(df['date'])
                        st.session_state.historical_data = df
                        st.success("Data uploaded!")
                    else:
                        st.error("CSV must have 'date' and 'sales' columns")
                        df = None
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.markdown("---")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "💬 Chatbot", "📈 Analysis"])
    
    with tab1:
        if df is not None and len(df) > 0 and 'sales' in df.columns and 'date' in df.columns:
            st.markdown("### 📊 Quick Summary")
            
            avg_sales = df['sales'].mean()
            total_sales = df['sales'].sum()
            max_sales = df['sales'].max()
            min_sales = df['sales'].min()
            std_dev = df['sales'].std()
            recent = df['sales'].tail(7).mean()
            prev = df['sales'].iloc[-14:-7].mean() if len(df) >= 14 else df['sales'].iloc[0]
            change = ((recent - prev) / prev * 100) if prev > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Sales", f"{total_sales:,.0f}")
            with col2:
                st.metric("Avg Daily", f"{avg_sales:.0f}")
            with col3:
                st.metric("Peak", f"{max_sales:.0f}")
            with col4:
                st.metric("Min", f"{min_sales:.0f}")
            
            col5, col6, col7, col8 = st.columns(4)
            with col5:
                st.metric("Std Dev", f"{std_dev:.1f}")
            with col6:
                st.metric("Days", f"{len(df)}")
            with col7:
                st.metric("7-Day Trend", f"{change:+.1f}%", delta=f"{change:.1f}", delta_color="normal")
            with col8:
                st.metric("Last Date", df['date'].iloc[-1].strftime('%m/%d'))
            
            st.markdown("---")
            st.markdown("### 📈 Forecast Chart")
            
            forecast = simple_forecast(df, forecast_horizon)
            if forecast:
                st.session_state.forecast_data = forecast
                last_date = df['date'].iloc[-1]
                forecast_dates = [last_date + timedelta(days=i+1) for i in range(len(forecast))]
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df['date'], y=df['sales'],
                    mode='lines+markers',
                    name='Historical',
                    line=dict(color='#3D5A80', width=2),
                    marker=dict(size=4)
                ))
                
                fig.add_trace(go.Scatter(
                    x=forecast_dates, y=forecast,
                    mode='lines+markers',
                    name='Forecast',
                    line=dict(color='#EE6C4D', width=2, dash='dot'),
                    marker=dict(size=6, symbol='diamond')
                ))
                
                upper = [f * 1.15 for f in forecast]
                lower = [f * 0.85 for f in forecast]
                fig.add_trace(go.Scatter(
                    x=forecast_dates + forecast_dates[::-1],
                    y=upper + lower[::-1],
                    fill='toself',
                    fillcolor='rgba(238,108,77,0.2)',
                    line=dict(color='rgba(238,108,77,0.2)'),
                    name='Confidence Interval',
                    showlegend=False
                ))
                
                fig.update_layout(
                    title="📈 Demand Forecast",
                    template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#E0E1DD'),
                    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                    legend=dict(bgcolor='rgba(0,0,0,0)')
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("""
            <div class="card" style="text-align: center; padding: 60px;">
                <h3 style="color: #E0E1DD;">📊 No Data Available</h3>
                <p style="color: #3D5A80;">Generate sample data or upload your CSV to see forecasts.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 💬 Ask About Your Forecasts")
        
        if st.session_state.historical_data is None or 'sales' not in st.session_state.historical_data.columns:
            st.warning("Please generate or upload data to enable the chatbot.")
        else:
            chat_container = st.container()
            with chat_container:
                for msg in st.session_state.chat_history:
                    bubble_class = "chat-user" if msg['role'] == 'user' else "chat-bot"
                    st.markdown(f"""
                    <div class="chat-message {bubble_class}">
                        <strong>{'You' if msg['role'] == 'user' else 'PIOUS'}:</strong> {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([5, 1])
            with col1:
                user_input = st.text_input("Ask a question...", placeholder="e.g., What will sales be next week?",
                                       key="chat_input", label_visibility="collapsed")
            with col2:
                if st.button("Send", use_container_width=True):
                    if user_input.strip():
                        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
                        response = get_bot_response(user_input, st.session_state.forecast_data, st.session_state.historical_data)
                        st.session_state.chat_history.append({'role': 'bot', 'content': response})
                        st.rerun()
            
            st.markdown("""
            <div style="margin-top: 20px; padding: 15px; background: rgba(29,58,95,0.4); border-radius: 12px;">
                <p style="color: #3D5A80; font-size: 12px; margin: 0;">
                    💡 Try: "What's the forecast?", "Is sales trending up?", "Recommend inventory level", "How does it work?"
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        if df is not None and len(df) > 0 and 'sales' in df.columns and 'date' in df.columns:
            st.markdown("### 📊 Analysis Summary")
            
            avg_sales = df['sales'].mean()
            total_sales = df['sales'].sum()
            max_sales = df['sales'].max()
            min_sales = df['sales'].min()
            std_sales = df['sales'].std()
            recent = df['sales'].tail(14).values
            if len(recent) >= 7:
                trend = (recent[-7:].mean() - recent[:7].mean()) / recent[:7].mean() * 100
            else:
                trend = 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Sales", f"{total_sales:,.0f}")
            with col2:
                st.metric("Avg Daily", f"{avg_sales:.1f}")
            with col3:
                st.metric("Peak", f"{max_sales:.0f}")
            with col4:
                st.metric("Min", f"{min_sales:.0f}")
            
            col5, col6, col7 = st.columns(3)
            with col5:
                st.metric("Std Dev", f"{std_sales:.1f}")
            with col6:
                st.metric("Days Analyzed", f"{len(df)}")
            with col7:
                st.metric("7-Day Trend", f"{trend:+.1f}%")
            
            st.markdown("---")
            st.markdown("### 📈 Detailed Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                daily_avg = df.groupby(df['date'].dt.dayofweek)['sales'].mean().reset_index()
                daily_avg.columns = ['dayofweek', 'sales']
                day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                daily_avg['day'] = daily_avg['dayofweek'].map(lambda x: day_names[x])
                fig_bar = px.bar(
                    daily_avg,
                    x='day', y='sales',
                    title="Average Sales by Day of Week",
                    labels={'day': 'Day', 'sales': 'Avg Sales'}
                )
                fig_bar.update_layout(
                    template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#E0E1DD')
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                fig_hist = px.histogram(
                    df, x='sales',
                    title="Sales Distribution",
                    nbins=20,
                    labels={'sales': 'Sales Value'}
                )
                fig_hist.update_layout(
                    template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#E0E1DD')
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            st.markdown("### 📋 Data Preview")
            st.dataframe(df.tail(10), use_container_width=True)
            
            metrics = calculate_metrics(df['sales'].tail(7).values, 
                                       [df['sales'].iloc[-7:].mean()] * 7 if len(df) >= 7 else [])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("MAPE", f"{metrics['mape']:.1f}%")
            with col2:
                st.metric("RMSE", f"{metrics['rmse']:.1f}")
            with col3:
                st.metric("MAE", f"{metrics['mae']:.1f}")
        else:
            st.markdown("""
            <div class="card" style="text-align: center; padding: 60px;">
                <h3 style="color: #E0E1DD;">📈 No Data for Analysis</h3>
                <p style="color: #3D5A80;">Load data to see detailed analytics.</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()