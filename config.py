import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "payments.db"
DB_PATH = os.path.join(BASE_DIR, DB_NAME)
MODEL_PATH = os.path.join(BASE_DIR, "risk_model.pkl")

# Simulation Settings
SIMULATION_DELAY = 0.1  # Seconds between transactions
FAILURE_RATE_NORMAL = 0.05
FAILURE_RATE_SPIKE = 0.40

# Risk Thresholds
RISK_THRESHOLD_HIGH = 0.7
RISK_THRESHOLD_MEDIUM = 0.4

# Entities
BANKS = ["HDFC", "SBI", "ICICI", "AXIS", "KOTAK"]
PSPS = ["GPay", "PhonePe", "Paytm", "AmazonPay", "BHIM"]
CHANNELS = ["P2P", "P2M", "QR"]
