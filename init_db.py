import sqlite3
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Transactions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            internal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            timestamp DATETIME,
            user_id TEXT,
            payer_bank TEXT,
            payee_bank TEXT,
            psp TEXT,
            amount REAL,
            channel TEXT,
            status TEXT,
            failure_reason TEXT,
            latency_ms REAL,
            risk_score REAL,
            decision TEXT,
            attempt_number INTEGER,
            geo TEXT,
            device_type TEXT
        )
    ''')

    # Entity Metrics Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entity_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bucket_start_time DATETIME,
            entity_type TEXT,
            entity_id TEXT,
            total_transactions INTEGER,
            successful_transactions INTEGER,
            failed_transactions INTEGER,
            avg_latency_ms REAL,
            failure_rate REAL
        )
    ''')

    # Alerts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_time DATETIME,
            entity_type TEXT,
            entity_id TEXT,
            alert_type TEXT,
            severity TEXT,
            details TEXT
        )
    ''')

    # Recovery Actions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recovery_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            action_type TEXT,
            old_route TEXT,
            new_route TEXT,
            status TEXT,
            timestamp DATETIME
        )
    ''')
    
    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_txn_timestamp ON transactions(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_txn_psp ON transactions(psp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_txn_bank ON transactions(payer_bank)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_txn_status ON transactions(status)')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
