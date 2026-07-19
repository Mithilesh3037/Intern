"""
Model Analysis Script
This script analyzes the trained .pkl model to extract:
- Feature names
- Number of features
- Model type
- Model coefficients
- Prediction output format
"""

import pickle
import os
import json

# Load the model
model_path = 'logistic_regression_spam_detector.pkl'

try:
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    print("=" * 70)
    print("MODEL ANALYSIS REPORT")
    print("=" * 70)
    
    # Model type
    print(f"\n1. MODEL TYPE: {type(model).__name__}")
    print(f"   Full Path: {type(model).__module__}.{type(model).__name__}")
    
    # Number of features
    if hasattr(model, 'n_features_in_'):
        print(f"\n2. NUMBER OF INPUT FEATURES: {model.n_features_in_}")
    else:
        print("\n2. NUMBER OF INPUT FEATURES: Could not determine directly")
    
    # Coefficients shape
    if hasattr(model, 'coef_'):
        print(f"\n3. MODEL COEFFICIENTS SHAPE: {model.coef_.shape}")
        print(f"   This means the model uses {model.coef_.shape[1]} features")
    
    # Intercept
    if hasattr(model, 'intercept_'):
        print(f"\n4. INTERCEPT VALUE: {model.intercept_}")
    
    # Classes (for classification)
    if hasattr(model, 'classes_'):
        print(f"\n5. PREDICTED CLASSES: {model.classes_}")
        print(f"   Class 0: {model.classes_[0]}")
        print(f"   Class 1: {model.classes_[1]}")
    
    # All attributes
    print(f"\n6. ALL MODEL ATTRIBUTES:")
    for attr in dir(model):
        if not attr.startswith('_'):
            try:
                value = getattr(model, attr)
                if not callable(value):
                    print(f"   - {attr}: {type(value).__name__}")
            except:
                pass
    
    print("\n" + "=" * 70)
    print("MODEL SUCCESSFULLY LOADED!")
    print("=" * 70)
    
except FileNotFoundError:
    print(f"ERROR: Model file not found at {model_path}")
    print("Please make sure the .pkl file is in the project root directory")
except Exception as e:
    print(f"ERROR: {str(e)}")
    print("Please check if the file is a valid pickle file")
