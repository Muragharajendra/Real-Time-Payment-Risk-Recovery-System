import threading
import queue
import time
import sqlite3
from simulator import TransactionSimulator
from aggregator import MetricsAggregator
from orchestrator import StreamingOrchestrator
from db_utils import get_db_connection

def verify_system():
    print("Starting Verification...")
    
    # 1. Check initial count
    conn = get_db_connection()
    initial_count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    conn.close()
    print(f"Initial transaction count: {initial_count}")

    # 2. Start System for 10 seconds
    txn_queue = queue.Queue()
    simulator = TransactionSimulator(txn_queue)
    aggregator = MetricsAggregator(interval=2) 
    orchestrator = StreamingOrchestrator(txn_queue)

    sim_thread = threading.Thread(target=simulator.run)
    agg_thread = threading.Thread(target=aggregator.run)
    orch_thread = threading.Thread(target=orchestrator.run)

    sim_thread.start()
    agg_thread.start()
    orch_thread.start()

    print("System running for 10 seconds...")
    time.sleep(10)

    # 3. Stop System
    simulator.stop()
    aggregator.stop()
    orchestrator.stop()
    
    sim_thread.join()
    agg_thread.join()
    orch_thread.join()

    # 4. Check final count
    conn = get_db_connection()
    final_count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    conn.close()
    print(f"Final transaction count: {final_count}")

    if final_count > initial_count:
        print("SUCCESS: New transactions were processed.")
    else:
        print("FAILURE: No new transactions found.")

if __name__ == "__main__":
    verify_system()
