import time
import random
import uuid
from datetime import datetime
from config import BANKS, PSPS, CHANNELS, SIMULATION_DELAY, FAILURE_RATE_NORMAL, FAILURE_RATE_SPIKE

class TransactionSimulator:
    def __init__(self, queue):
        self.queue = queue
        self.running = True
        self.users = [f"user_{i}" for i in range(1, 101)]

    def generate_transaction(self):
        transaction_id = str(uuid.uuid4())
        user_id = random.choice(self.users)
        payer_bank = random.choice(BANKS)
        payee_bank = random.choice(BANKS)
        while payee_bank == payer_bank:
            payee_bank = random.choice(BANKS)
        
        psp = random.choice(PSPS)
        amount = round(random.uniform(10, 5000), 2)
        channel = random.choice(CHANNELS)
        geo = random.choice(["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"])
        device_type = random.choice(["Android", "iOS"])
        
        # Simulate controlled failure/latency patterns
        # Example: 10% chance of a "bad" PSP state causing higher failure rates
        is_bad_state = random.random() < 0.1
        
        return {
            "transaction_id": transaction_id,
            "timestamp": datetime.now(),
            "user_id": user_id,
            "payer_bank": payer_bank,
            "payee_bank": payee_bank,
            "psp": psp,
            "amount": amount,
            "channel": channel,
            "geo": geo,
            "device_type": device_type,
            "attempt_number": 1,
            "status": "PENDING",
            "is_bad_state": is_bad_state # Internal flag for simulation logic
        }

    def run(self):
        print("Simulator started...")
        while self.running:
            txn = self.generate_transaction()
            self.queue.put(txn)
            time.sleep(SIMULATION_DELAY)

    def stop(self):
        self.running = False
