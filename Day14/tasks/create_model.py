import pickle
from pathlib import Path

from app import SimpleMLModel


model_path = Path("models/simple_model.pkl")
with model_path.open("wb") as file:
    pickle.dump(SimpleMLModel(), file)

print(f"Model saved to {model_path}")
