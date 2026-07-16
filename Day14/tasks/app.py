from pathlib import Path
import pickle

from flask import Flask, render_template, request

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
MODEL_CANDIDATES = []
    MODELS_DIR / "diabetes_model.pkl",
    MODELS_DIR / "your_model.pkl",
    MODELS_DIR / "simple_model.pkl",


FEATURES = [
    {"name": "Pregnancies", "label": "Pregnancies", "type": "number"},
    {"name": "Glucose", "label": "Glucose", "type": "number"},
    {"name": "BloodPressure", "label": "Blood Pressure", "type": "number"},
    {"name": "SkinThickness", "label": "Skin Thickness", "type": "number"},
    {"name": "Insulin", "label": "Insulin", "type": "number"},
    {"name": "BMI", "label": "BMI", "type": "number"},
    {"name": "DiabetesPedigreeFunction", "label": "Diabetes Pedigree Function", "type": "number"},
    {"name": "Age", "label": "Age", "type": "number"},
]


class SimpleDiabetesModel:
    def predict(self, features):
        results = []
        for value_list in features:
            pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, pedigree, age = value_list
            risk_score = 0.0
            risk_score += max(0, glucose - 140) / 30
            risk_score += max(0, bmi - 25) / 10
            risk_score += max(0, age - 40) / 10
            risk_score += max(0, pregnancies - 2) / 3
            risk_score += max(0, pedigree - 0.5) / 0.5
            result = "High Risk" if risk_score >= 2.2 else "Low Risk"
            results.append(result)
        return results


def load_model():
    for candidate in MODEL_CANDIDATES:
        if candidate.exists():
            try:
                with open(candidate, "rb") as file:
                    return pickle.load(file)
            except Exception:
                continue

    return SimpleDiabetesModel()


MODEL = load_model()


def prepare_input_values(form_data):
    values = []
    for field in FEATURES:
        raw_value = form_data.get(field["name"], "")
        try:
            values.append(float(raw_value))
        except ValueError:
            values.append(0.0)
    return [values]


@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None
    error_message = None

    if request.method == "POST":
        try:
            values = prepare_input_values(request.form)
            prediction = MODEL.predict(values)[0]
        except Exception as exc:
            error_message = f"Prediction failed: {exc}"

        return render_template(
            "result.html",
            prediction=prediction,
            error_message=error_message,
            features=FEATURES,
        )

    return render_template("index.html", features=FEATURES, model_loaded=MODEL is not None)


if __name__ == "__main__":
    app.run(debug=True)
