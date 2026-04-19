# PIOUS - Demand Forecasting AI Agent

A Streamlit-based demand forecasting application with an interactive chatbot.

## Features

- **Dashboard**: View key metrics (avg sales, trend, peak demand, volatility) and forecast charts
- **Chatbot**: Ask questions about your forecasts in natural language
- **Analysis**: Detailed analytics with day-of-week patterns and distribution charts

## Installation

```bash
pip install -r requirements.txt
```

## Running the App

```bash
streamlit run app.py
```

Or:

```bash
python -m streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Data Format

Upload a CSV file with two columns:
- `date`: Date in YYYY-MM-DD format
- `sales`: Numeric sales value

Example:
```csv
date,sales
2024-01-01,150
2024-01-02,165
...
```

## Chatbot Commands

Try asking:
- "What's the forecast?"
- "Is sales trending up?"
- "Recommend inventory level"
- "What will sales be next week?"
- "How does it work?"

## Technologies

- Streamlit
- Pandas
- NumPy
- Plotly