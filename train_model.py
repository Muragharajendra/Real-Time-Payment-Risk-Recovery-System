import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from db_utils import get_db_connection
from config import MODEL_PATH

def train_model():
    print("Loading data from SQLite...")
    conn = get_db_connection()
    query = "SELECT amount, channel, geo, device_type, status FROM transactions"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("No data found to train model.")
        return

    # Create Label: 1 if FAILURE, 0 if SUCCESS
    df['label'] = df['status'].apply(lambda x: 1 if x == 'FAILURE' else 0)
    
    X = df[['amount', 'channel', 'geo', 'device_type']]
    y = df['label']

    # Preprocessing
    categorical_features = ['channel', 'geo', 'device_type']
    numerical_features = ['amount']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', SimpleImputer(strategy='median'), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])

    # Pipeline
    clf = Pipeline(steps=[('preprocessor', preprocessor),
                          ('classifier', RandomForestClassifier(n_estimators=50, random_state=42))])

    # Train
    print("Training model...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf.fit(X_train, y_train)

    # Evaluate
    score = clf.score(X_test, y_test)
    print(f"Model Accuracy: {score:.2f}")

    # Save
    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_model()
