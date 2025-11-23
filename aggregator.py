import time
import pandas as pd
from datetime import datetime, timedelta
from db_utils import execute_query, fetch_query, get_db_connection

class MetricsAggregator:
    def __init__(self, interval=30):
        self.interval = interval
        self.running = True

    def compute_metrics(self):
        # Look back 1 minute
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=1)
        
        conn = get_db_connection()
        query = '''
            SELECT 
                payer_bank, psp, status, latency_ms 
            FROM transactions 
            WHERE timestamp BETWEEN ? AND ?
        '''
        df = pd.read_sql_query(query, conn, params=(start_time, end_time))
        conn.close()

        if df.empty:
            return

        # Aggregate by Bank
        bank_stats = df.groupby('payer_bank').agg(
            total=('status', 'count'),
            success=('status', lambda x: (x == 'SUCCESS').sum()),
            failed=('status', lambda x: (x == 'FAILURE').sum()),
            avg_latency=('latency_ms', 'mean')
        ).reset_index()

        for _, row in bank_stats.iterrows():
            failure_rate = row['failed'] / row['total'] if row['total'] > 0 else 0
            self.save_metrics(start_time, 'BANK', row['payer_bank'], row['total'], row['success'], row['failed'], row['avg_latency'], failure_rate)

        # Aggregate by PSP
        psp_stats = df.groupby('psp').agg(
            total=('status', 'count'),
            success=('status', lambda x: (x == 'SUCCESS').sum()),
            failed=('status', lambda x: (x == 'FAILURE').sum()),
            avg_latency=('latency_ms', 'mean')
        ).reset_index()

        for _, row in psp_stats.iterrows():
            failure_rate = row['failed'] / row['total'] if row['total'] > 0 else 0
            self.save_metrics(start_time, 'PSP', row['psp'], row['total'], row['success'], row['failed'], row['avg_latency'], failure_rate)

    def save_metrics(self, bucket_start, entity_type, entity_id, total, success, failed, avg_latency, failure_rate):
        query = '''
            INSERT INTO entity_metrics 
            (bucket_start_time, entity_type, entity_id, total_transactions, successful_transactions, failed_transactions, avg_latency_ms, failure_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        execute_query(query, (bucket_start, entity_type, entity_id, int(total), int(success), int(failed), float(avg_latency) if pd.notnull(avg_latency) else 0.0, float(failure_rate)))

    def run(self):
        print("Metrics Aggregator started...")
        while self.running:
            try:
                self.compute_metrics()
            except Exception as e:
                print(f"Error in aggregator: {e}")
            time.sleep(self.interval)

    def stop(self):
        self.running = False
