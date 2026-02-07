import pandas as pd
import numpy as np

np.random.seed(42)

data = []

for _ in range(5000):
    amount = np.random.randint(100, 100000)
    txn_count = np.random.randint(1, 30)
    distance = np.random.randint(1, 10000)
    ip_risk = np.random.randint(1, 100)
    failed_logins = np.random.randint(0, 5)

    # FRAUD LOGIC (realistic pattern)
    fraud = 1 if (
        amount > 50000 and
        distance > 2000 and
        ip_risk > 60
    ) else 0

    data.append([amount, txn_count, distance, ip_risk, failed_logins, fraud])

df = pd.DataFrame(data, columns=[
    "amount", "txn_count", "distance", "ip_risk", "failed_logins", "fraud"
])

df.to_csv("transactions.csv", index=False)
print("Dataset generated: transactions.csv")
