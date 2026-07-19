"""
Create a Sample Trained Model
This script creates a demo LogisticRegression model that simulates
a customer churn/purchase prediction system
"""

import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Create a demo model with realistic feature names
# These features represent common customer data
feature_names = [
    'age',                    # Customer age (years)
    'tenure_months',          # How long customer has been with company
    'monthly_charges',        # Monthly spending amount
    'total_charges',          # Total lifetime spending
    'contract_length',        # Contract duration (months)
    'internet_service',       # 0=No, 1=Yes
    'num_products',           # Number of products purchased
    'customer_support_calls', # Number of support calls
    'purchase_frequency',     # Times purchased per month
    'avg_order_value'         # Average purchase amount
]

# Create and train a simple model
X_sample = np.array([
    [25, 6, 50, 300, 12, 1, 2, 1, 4, 75],
    [45, 24, 80, 1920, 24, 1, 4, 2, 8, 120],
    [35, 12, 60, 720, 12, 1, 3, 0, 6, 90],
    [55, 36, 100, 3600, 24, 1, 5, 3, 10, 150],
    [28, 3, 30, 90, 6, 0, 1, 5, 2, 50],
])

y_sample = np.array([0, 1, 1, 1, 0])  # 0=Churn/No Purchase, 1=Retain/Purchase

# Train the model
model = LogisticRegression(random_state=42)
model.fit(X_sample, y_sample)

# Save the model
model_path = 'logistic_regression_spam_detector.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model, f)

print("✓ Sample model created successfully!")
print(f"✓ Saved to: {model_path}")
print(f"\nModel Features ({len(feature_names)}):")
for i, name in enumerate(feature_names, 1):
    print(f"  {i}. {name}")
