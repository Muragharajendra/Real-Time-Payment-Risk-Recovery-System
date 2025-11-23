import threading
import queue
import time
from simulator import TransactionSimulator
from aggregator import MetricsAggregator
from orchestrator import StreamingOrchestrator

def main():
    print("Starting Real-Time Payment Risk & Recovery System...")
    
    # Shared Queue
    txn_queue = queue.Queue()

    # Components
    simulator = TransactionSimulator(txn_queue)
    aggregator = MetricsAggregator(interval=10) # Run every 10s for demo
    orchestrator = StreamingOrchestrator(txn_queue)

    # Threads
    sim_thread = threading.Thread(target=simulator.run)
    agg_thread = threading.Thread(target=aggregator.run)
    orch_thread = threading.Thread(target=orchestrator.run)

    # Start
    sim_thread.start()
    agg_thread.start()
    orch_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping system...")
        simulator.stop()
        aggregator.stop()
        orchestrator.stop()
        
        sim_thread.join()
        agg_thread.join()
        orch_thread.join()
        print("System stopped.")

if __name__ == "__main__":
    main()
