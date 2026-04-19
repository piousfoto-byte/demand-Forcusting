# Demand Forecasting AI Agent with Chatbot

## Project Overview
- **Project Name**: PIOUS - Demand Forecasting Assistant
- **Type**: Streamlit Web Application with AI Agent
- **Core Functionality**: A demand forecasting tool with an interactive chatbot that helps users analyze sales data, generate forecasts, and get insights
- **Target Users**: Business analysts, inventory managers, supply chain professionals

## UI/UX Specification

### Layout Structure
- **Sidebar**: Navigation, settings, and model configuration
- **Main Area**: Dashboard with tabs for Forecast, Chatbot, and Data Analysis
- **Responsive**: Single column on mobile, multi-column on desktop

### Visual Design
- **Color Palette**:
  - Primary: #1E3A5F (Deep Navy)
  - Secondary: #3D5A80 (Steel Blue)
  - Accent: #EE6C4D (Coral Orange)
  - Background: #0D1B2A (Dark Blue)
  - Surface: #1B2838 (Dark Slate)
  - Text: #E0E1DD (Light Gray)
  - Success: #4ECDC4 (Teal)
  - Warning: #FFD166 (Amber)

- **Typography**:
  - Headings: "Orbitron", sans-serif (futuristic feel)
  - Body: "Inter", sans-serif
  - Code/Numbers: "JetBrains Mono", monospace

- **Spacing**: 8px base unit, multiples of 8 for padding/margins

- **Visual Effects**:
  - Glassmorphism cards with subtle blur
  - Smooth transitions on hover
  - Subtle glow effects on interactive elements

### Components
1. **Metric Cards**: Display KPIs with icons and trend indicators
2. **Charts**: Line charts for forecasts, bar charts for comparisons
3. **Chat Interface**: Message bubbles with timestamps
4. **Data Tables**: Sortable, filterable tables
5. **Upload Zone**: Drag-and-drop file upload
6. **Buttons**: Gradient buttons with hover animations

## Functionality Specification

### Core Features

#### 1. Data Management
- Upload CSV/Excel files with historical sales data
- Sample dataset generation for demo
- Data preview and validation
- Date range selection

#### 2. Demand Forecasting
- Time series forecasting using Prophet-like approach
- Multiple forecast horizons (7, 14, 30 days)
- Confidence intervals display
- Seasonality detection

#### 3. AI Chatbot
- Natural language queries about forecasts
- Ask questions like "What will sales be next week?"
- Explain forecast methodology
- Provide insights and recommendations
- Context-aware responses based on current data

#### 4. Analytics Dashboard
- Historical trend visualization
- Forecast vs actual comparison
- Key metrics: MAPE, RMSE, trend direction
- Anomaly detection alerts

### User Interactions
- File upload triggers data processing
- Click on chart points for details
- Type in chatbot for predictions/insights
- Adjust forecast parameters via sliders

### Data Handling
- Pandas for data manipulation
- Simulated ML model (ensemble of simple predictors)
- Session state for conversation history

## Acceptance Criteria
1. App loads without errors
2. File upload works and displays data preview
3. Forecast generates and displays chart
4. Chatbot responds to queries with relevant answers
5. UI is responsive and visually polished
6. No console errors in production