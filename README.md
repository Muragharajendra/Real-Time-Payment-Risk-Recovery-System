# Real-Time Payment Risk & Recovery System

A simulated real-time payment processing system with risk detection, recovery logic, and a live dashboard.

## Tech Stack
- **Language**: Python 3.8+
- **Database**: SQLite
- **ML**: Scikit-learn (Random Forest)
- **Dashboard**: Streamlit
- **Visualization**: Plotly

## Components
1.  **Transaction Simulator**: Generates synthetic UPI transactions with controlled failure patterns.
2.  **Streaming Orchestrator**: Consumes transactions, applies ML risk scoring, and executes recovery actions (Retries/Route Changes).
3.  **Metrics Aggregator**: Computes real-time stats for Banks and PSPs.
4.  **Offline ML Training**: Trains a risk model on historical data.
5.  **Dashboard**: Visualizes system health, funnels, and alerts.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Initialize Database**:
    ```bash
    python init_db.py
    ```

3.  **Generate Data & Train Model**:
    ```bash
    python generate_data.py
    python train_model.py
    ```

## Running the System

1.  **Start the Streaming Engine**:
    ```bash
    python main.py
    ```
    This will start the Simulator, Orchestrator, and Aggregator threads. You will see logs in the console.

2.  **Start the Dashboard**:
    Open a new terminal and run:
    ```bash
    python -m streamlit run dashboard.py
    ```
    Access the dashboard at `http://localhost:8501`.

## Dashboard Pages
- **Live Overview**: Real-time transaction volume and success/failure rates.
- **Bank & PSP Health**: Time-series charts of failure rates and latency for specific entities.
- **Conversion Funnel**: Visualizes the flow from initiation to success, showing drop-offs at risk detection and recovery.
- **Risk & Alerts**: Lists high-risk transactions and system alerts.
- **Recovery Effectiveness**: Shows the outcome of automated retries and route changes.
