import random
import uuid
from datetime import datetime, timedelta
from db_utils import execute_query
from config import BANKS, PSPS, CHANNELS

def generate_historical_data(num_records=1000):
    print(f"Generating {num_records} historical records...")
    
    users = [f"user_{i}" for i in range(1, 101)]
    
    for _ in range(num_records):
        transaction_id = str(uuid.uuid4())
        # Random time in last 24 hours
        timestamp = datetime.now() - timedelta(minutes=random.randint(0, 1440))
        user_id = random.choice(users)
        payer_bank = random.choice(BANKS)
        payee_bank = random.choice(BANKS)
        psp = random.choice(PSPS)
        amount = round(random.uniform(10, 5000), 2)
        channel = random.choice(CHANNELS)
        geo = random.choice(["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"])
        device_type = random.choice(["Android", "iOS"])
        
        # Simulate outcome
        if random.random() < 0.1:
            status = "FAILURE"
            failure_reason = "TIMEOUT"
            latency = random.uniform(2000, 5000)
            risk_score = random.uniform(0.6, 0.9)
        else:
            status = "SUCCESS"
            failure_reason = None
            latency = random.uniform(100, 800)
            risk_score = random.uniform(0.0, 0.4)

        query = '''
            INSERT INTO transactions 
            (transaction_id, timestamp, user_id, payer_bank, payee_bank, psp, amount, channel, status, failure_reason, latency_ms, risk_score, geo, device_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        execute_query(query, (transaction_id, timestamp, user_id, payer_bank, payee_bank, psp, amount, channel, status, failure_reason, latency, risk_score, geo, device_type))

    print("Data generation complete.")

if __name__ == "__main__":
    generate_historical_data()
