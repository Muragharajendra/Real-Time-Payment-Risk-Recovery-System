import time
import queue
import threading
import random
from datetime import datetime, timedelta
from db_utils import execute_query, fetch_query
from inference import RiskModel
from config import RISK_THRESHOLD_HIGH, RISK_THRESHOLD_MEDIUM

class StreamingOrchestrator:
    def __init__(self, input_queue):
        self.input_queue = input_queue
        self.running = True
        self.risk_model = RiskModel()

    def process_event(self, event):
        # 1. Ingestion
        self.ingest_transaction(event)

        # 2. Status Simulation (Simulate latency and outcome)
        # In a real system, this would be async, but here we simulate it immediately
        self.simulate_outcome(event)

        # 3. Context Fetching (Simplified: we rely on what's in the event + model)
        # In a real system, we'd query entity_metrics here for rules.

        # 4. Risk Scoring
        risk_score = self.risk_model.predict(event)
        event['risk_score'] = risk_score

        # 5. Decision & Recovery
        decision, recovery_action = self.make_decision(event, risk_score)
        event['decision'] = decision

        # 6. Update Transaction with Risk & Decision
        self.update_transaction_decision(event)

        # 7. Execute Recovery (if any)
        if recovery_action:
            self.execute_recovery(event, recovery_action)

        # 8. Alerting
        if risk_score > RISK_THRESHOLD_HIGH:
            self.create_alert(event, "HIGH_RISK_TRANSACTION", "High risk score detected")

    def ingest_transaction(self, event):
        query = '''
            INSERT INTO transactions 
            (transaction_id, timestamp, user_id, payer_bank, payee_bank, psp, amount, channel, status, attempt_number, geo, device_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        execute_query(query, (
            event['transaction_id'], event['timestamp'], event['user_id'], 
            event['payer_bank'], event['payee_bank'], event['psp'], 
            event['amount'], event['channel'], event['status'], 
            event['attempt_number'], event['geo'], event['device_type']
        ))

    def simulate_outcome(self, event):
        # Use the flag from simulator or random logic
        if event.get('is_bad_state', False) or random.random() < 0.05:
            event['status'] = 'FAILURE'
            event['failure_reason'] = 'TIMEOUT'
            event['latency_ms'] = random.uniform(2000, 5000)
        else:
            event['status'] = 'SUCCESS'
            event['failure_reason'] = None
            event['latency_ms'] = random.uniform(100, 800)
        
        # Update DB
        query = "UPDATE transactions SET status = ?, failure_reason = ?, latency_ms = ? WHERE transaction_id = ?"
        execute_query(query, (event['status'], event['failure_reason'], event['latency_ms'], event['transaction_id']))

    def make_decision(self, event, risk_score):
        decision = "ALLOW"
        recovery_action = None

        if risk_score > RISK_THRESHOLD_HIGH:
            decision = "ROUTE_CHANGE"
            recovery_action = "ROUTE_CHANGE"
        elif risk_score > RISK_THRESHOLD_MEDIUM and event['status'] == 'FAILURE':
            decision = "RETRY"
            recovery_action = "RETRY"
        elif event['status'] == 'FAILURE':
             # Simple retry for failures even if low risk, up to a limit
             if event['attempt_number'] < 3:
                 decision = "RETRY"
                 recovery_action = "RETRY"
             else:
                 decision = "BLOCK" # Or just failed final

        return decision, recovery_action

    def update_transaction_decision(self, event):
        query = "UPDATE transactions SET risk_score = ?, decision = ? WHERE transaction_id = ?"
        execute_query(query, (event['risk_score'], event['decision'], event['transaction_id']))

    def execute_recovery(self, event, action_type):
        # Log recovery action
        new_route = None
        if action_type == "ROUTE_CHANGE":
            # Simple logic: pick a different PSP
            available_psps = ["GPay", "PhonePe", "Paytm", "AmazonPay", "BHIM"]
            if event['psp'] in available_psps:
                available_psps.remove(event['psp'])
            new_route = random.choice(available_psps)
        
        query = '''
            INSERT INTO recovery_actions (transaction_id, action_type, old_route, new_route, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        execute_query(query, (event['transaction_id'], action_type, event['psp'], new_route, "INITIATED", datetime.now()))

        # In a real system, we would push a new event to the queue here.
        # For simulation, let's just print it.
        # print(f"Recovery Action: {action_type} for {event['transaction_id']} -> New Route: {new_route}")

    def create_alert(self, event, alert_type, details):
        query = '''
            INSERT INTO alerts (created_time, entity_type, entity_id, alert_type, severity, details)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        execute_query(query, (datetime.now(), "TRANSACTION", event['transaction_id'], alert_type, "HIGH", details))

    def run(self):
        print("Orchestrator started...")
        while self.running:
            try:
                event = self.input_queue.get(timeout=1)
                self.process_event(event)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in orchestrator: {e}")

    def stop(self):
        self.running = False
