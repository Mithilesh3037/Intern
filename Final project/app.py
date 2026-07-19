"""
CartSense – Customer Purchase & Churn Predictor
================================================
Flask Web Application  |  Module 3 & 4 – Internship Final Project

Architecture:
  - Flask backend with Jinja2 templates
  - SQLite database for customer records & prediction history
  - Logistic Regression model (17 features) via joblib
  - REST API endpoints for AJAX interactions
  - Render-compatible (reads PORT env variable)

Author: Mithilesh Kumaresan
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import os, json, warnings, logging
from datetime import datetime
import sqlite3
import numpy as np
import joblib
from flask import (Flask, render_template, request, jsonify,
                   redirect, url_for, flash, abort, session)
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s – %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("cartsense")

# ── App init ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cartsense-dev-secret-2024")


def login_required(f):
    """Decorator: redirect to login if not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH   = os.path.join(BASE_DIR, "customers.db")
PKL_PATH  = os.path.join(BASE_DIR, "cartsense_model.pkl")

# ── Feature configuration (17 placeholder features — swap names when known) ───
FEATURE_CONFIG = [
    {"key": "f1",  "label": "Feature 1",  "description": "Customer metric 1",  "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
    {"key": "f2",  "label": "Feature 2",  "description": "Customer metric 2",  "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
    {"key": "f3",  "label": "Feature 3",  "description": "Customer metric 3",  "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
    {"key": "f4",  "label": "Feature 4",  "description": "Customer metric 4",  "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
    {"key": "f5",  "label": "Feature 5",  "description": "Customer metric 5",  "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
    {"key": "f6",  "label": "Feature 6",  "description": "Customer metric 6",  "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
    {"key": "f7",  "label": "Feature 7",  "description": "Customer metric 7",  "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
    {"key": "f8",  "label": "Feature 8",  "description": "Customer metric 8",  "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
    {"key": "f9",  "label": "Feature 9",  "description": "Customer metric 9",  "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
    {"key": "f10", "label": "Feature 10", "description": "Customer metric 10", "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
    {"key": "f11", "label": "Feature 11", "description": "Customer metric 11", "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
    {"key": "f12", "label": "Feature 12", "description": "Customer metric 12", "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
    {"key": "f13", "label": "Feature 13", "description": "Customer metric 13", "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
    {"key": "f14", "label": "Feature 14", "description": "Customer metric 14", "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
    {"key": "f15", "label": "Feature 15", "description": "Customer metric 15", "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
    {"key": "f16", "label": "Feature 16", "description": "Customer metric 16", "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
    {"key": "f17", "label": "Feature 17", "description": "Customer metric 17", "type": "float", "min": 0, "max": 1000, "step": "0.01", "default": 0},
]
FEATURE_KEYS = [f["key"] for f in FEATURE_CONFIG]

# ── ML Model ──────────────────────────────────────────────────────────────────
_model       = None
_model_error = None

def load_model():
    global _model, _model_error
    try:
        _model = joblib.load(PKL_PATH)
        log.info("Model loaded: %s  |  features=%d  classes=%s",
                 PKL_PATH, _model.n_features_in_, _model.classes_)
    except Exception as e:
        _model_error = str(e)
        log.error("Model load failed: %s", e)

load_model()

def run_prediction(feature_values: list):
    """Run model inference. Returns (prediction_int, churn_prob, retain_prob)."""
    if _model is None:
        raise RuntimeError(f"Model not loaded: {_model_error}")
    X    = np.array(feature_values, dtype=float).reshape(1, -1)
    pred = int(_model.predict(X)[0])
    prob = _model.predict_proba(X)[0].tolist()   # [P(class0), P(class1)]
    churn_prob  = round(prob[1] * 100, 2)
    retain_prob = round(prob[0] * 100, 2)
    return pred, churn_prob, retain_prob

# ── Database ──────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            name              TEXT    NOT NULL,
            email             TEXT    NOT NULL UNIQUE,
            phone             TEXT,
            company           TEXT,
            segment           TEXT    DEFAULT 'General',
            f1  REAL DEFAULT 0, f2  REAL DEFAULT 0, f3  REAL DEFAULT 0,
            f4  REAL DEFAULT 0, f5  REAL DEFAULT 0, f6  REAL DEFAULT 0,
            f7  REAL DEFAULT 0, f8  REAL DEFAULT 0, f9  REAL DEFAULT 0,
            f10 REAL DEFAULT 0, f11 REAL DEFAULT 0, f12 REAL DEFAULT 0,
            f13 REAL DEFAULT 0, f14 REAL DEFAULT 0, f15 REAL DEFAULT 0,
            f16 REAL DEFAULT 0, f17 REAL DEFAULT 0,
            prediction        INTEGER,
            churn_probability REAL,
            retain_probability REAL,
            risk_level        TEXT,
            notes             TEXT,
            created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS prediction_history (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id       INTEGER REFERENCES customers(id) ON DELETE CASCADE,
            customer_name     TEXT,
            customer_email    TEXT,
            prediction        INTEGER,
            churn_probability REAL,
            retain_probability REAL,
            risk_level        TEXT,
            feature_snapshot  TEXT,
            triggered_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL UNIQUE,
            name       TEXT,
            email      TEXT UNIQUE,
            password   TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
    # Seed default admin account if users table is empty
    with get_db() as conn:
        exists = conn.execute("SELECT id FROM users WHERE username='admin'").fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO users (username, name, email, password) VALUES (?, ?, ?, ?)",
                ["admin", "Administrator", "admin@cartsense.ai",
                 generate_password_hash("cartsense123")]
            )
            log.info("Default admin account seeded.")
    log.info("Database ready: %s", DB_PATH)

init_db()

def row_to_dict(row):
    return dict(row) if row else None

def rows_to_list(rows):
    return [dict(r) for r in rows]

def risk_label(churn_prob: float) -> str:
    if churn_prob >= 70:  return "High"
    if churn_prob >= 40:  return "Medium"
    return "Low"

# ── Auth Routes ───────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page — GET shows form, POST validates credentials against users table."""
    if session.get("logged_in"):
        return redirect(url_for("landing"))
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username=?", (username,)
            ).fetchone()
        if user and check_password_hash(user["password"], password):
            session["logged_in"] = True
            session["username"]   = user["username"]
            session["user_name"]  = user["name"] or user["username"]
            log.info("User '%s' logged in.", username)
            return redirect(url_for("landing"))
        error = "Invalid user ID or password. Please try again."
        log.warning("Failed login attempt for user '%s'.", username)
    return render_template("login.html", error=error, mode="login")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Create a new account."""
    if session.get("logged_in"):
        return redirect(url_for("landing"))
    error = None
    if request.method == "POST":
        name     = request.form.get("name",     "").strip()
        username = request.form.get("username", "").strip()
        email    = request.form.get("email",    "").strip()
        password = request.form.get("password", "").strip()
        confirm  = request.form.get("confirm",  "").strip()

        if not name or not username or not password:
            error = "Full name, user ID, and password are required."
        elif len(username) < 3:
            error = "User ID must be at least 3 characters."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif password != confirm:
            error = "Passwords do not match."
        else:
            try:
                with get_db() as conn:
                    conn.execute(
                        "INSERT INTO users (username, name, email, password) VALUES (?,?,?,?)",
                        [username, name, email or None,
                         generate_password_hash(password)]
                    )
                session["logged_in"] = True
                session["username"]  = username
                session["user_name"] = name
                log.info("New account created: '%s'.", username)
                return redirect(url_for("landing"))
            except Exception:
                error = "User ID or email already exists. Please choose another."
    return render_template("login.html", error=error, mode="register")

@app.route("/logout")
def logout():
    """Clear session and redirect to login."""
    session.clear()
    return redirect(url_for("login"))

# ── Page Routes ───────────────────────────────────────────────────────────────
@app.route("/")
@login_required
def landing():
    """Professional landing / home page."""
    return render_template("index.html")

@app.route("/about")
@login_required
def about():
    return render_template("about.html")

@app.route("/predict", methods=["GET"])
@login_required
def predict_form():
    """Churn prediction form page."""
    return render_template("predict.html",
                           features=FEATURE_CONFIG,
                           model_ok=_model is not None)

@app.route("/predict", methods=["POST"])
@login_required
def predict_submit():
    """Handle form submission → run model → show result page."""
    try:
        name    = request.form.get("name", "").strip()
        email   = request.form.get("email", "").strip()
        phone   = request.form.get("phone", "").strip()
        company = request.form.get("company", "").strip()
        segment = request.form.get("segment", "General").strip()
        notes   = request.form.get("notes", "").strip()

        if not name or not email:
            flash("Customer name and email are required.", "error")
            return redirect(url_for("predict_form"))

        fvals = []
        for k in FEATURE_KEYS:
            try:
                fvals.append(float(request.form.get(k, 0)))
            except (TypeError, ValueError):
                fvals.append(0.0)

        pred, churn_prob, retain_prob = run_prediction(fvals)
        risk = risk_label(churn_prob)

        snapshot = json.dumps({k: v for k, v in zip(FEATURE_KEYS, fvals)})

        # Save / upsert customer
        with get_db() as conn:
            existing = conn.execute("SELECT id FROM customers WHERE email=?", (email,)).fetchone()
            if existing:
                cid = existing["id"]
                cols = ", ".join(f"{k}=?" for k in FEATURE_KEYS)
                conn.execute(f"""UPDATE customers SET
                    name=?, phone=?, company=?, segment=?, {cols},
                    prediction=?, churn_probability=?, retain_probability=?,
                    risk_level=?, notes=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?""",
                    [name, phone, company, segment, *fvals,
                     pred, churn_prob, retain_prob, risk, notes, cid])
            else:
                cur = conn.execute(f"""INSERT INTO customers
                    (name,email,phone,company,segment,{','.join(FEATURE_KEYS)},
                     prediction,churn_probability,retain_probability,risk_level,notes)
                    VALUES (?,?,?,?,?,{','.join(['?']*17)},?,?,?,?,?)""",
                    [name, email, phone, company, segment, *fvals,
                     pred, churn_prob, retain_prob, risk, notes])
                cid = cur.lastrowid

            # Log to history
            conn.execute("""INSERT INTO prediction_history
                (customer_id,customer_name,customer_email,prediction,
                 churn_probability,retain_probability,risk_level,feature_snapshot)
                VALUES (?,?,?,?,?,?,?,?)""",
                [cid, name, email, pred, churn_prob, retain_prob, risk, snapshot])

        return redirect(url_for("result_page", cid=cid))

    except Exception as e:
        log.error("Prediction submit error: %s", e)
        flash(f"Prediction failed: {e}", "error")
        return redirect(url_for("predict_form"))

@app.route("/result/<int:cid>")
@login_required
def result_page(cid):
    """Show churn prediction result for a customer."""
    with get_db() as conn:
        c = row_to_dict(conn.execute("SELECT * FROM customers WHERE id=?", (cid,)).fetchone())
    if not c:
        abort(404)
    return render_template("result.html", customer=c, features=FEATURE_CONFIG)

@app.route("/dashboard")
@login_required
def dashboard():
    """Customer Analytics Dashboard."""
    with get_db() as conn:
        customers = rows_to_list(conn.execute(
            "SELECT * FROM customers ORDER BY updated_at DESC").fetchall())
        total     = len(customers)
        churned   = sum(1 for c in customers if c["prediction"] == 1)
        retained  = total - churned
        high_risk = sum(1 for c in customers if c.get("risk_level") == "High")
        avg_churn = (sum(c["churn_probability"] or 0 for c in customers) / total) if total else 0

    return render_template("dashboard.html",
        customers=customers, total=total, churned=churned,
        retained=retained, high_risk=high_risk,
        avg_churn=round(avg_churn, 1))

@app.route("/customers")
@login_required
def customers_list():
    """Customer Records Management page."""
    q       = request.args.get("q", "").strip()
    risk_f  = request.args.get("risk", "").strip()
    pred_f  = request.args.get("pred", "").strip()
    seg_f   = request.args.get("segment", "").strip()

    sql  = "SELECT * FROM customers WHERE 1=1"
    args = []
    if q:
        sql += " AND (name LIKE ? OR email LIKE ? OR company LIKE ?)"
        args += [f"%{q}%", f"%{q}%", f"%{q}%"]
    if risk_f:
        sql += " AND risk_level=?"
        args.append(risk_f)
    if pred_f in ("0", "1"):
        sql += " AND prediction=?"
        args.append(int(pred_f))
    if seg_f:
        sql += " AND segment=?"
        args.append(seg_f)
    sql += " ORDER BY updated_at DESC"

    with get_db() as conn:
        customers = rows_to_list(conn.execute(sql, args).fetchall())
        segments  = [r[0] for r in conn.execute(
            "SELECT DISTINCT segment FROM customers WHERE segment IS NOT NULL").fetchall()]

    return render_template("customers.html",
        customers=customers, q=q, risk_f=risk_f,
        pred_f=pred_f, seg_f=seg_f, segments=segments)

@app.route("/customers/<int:cid>/edit", methods=["GET", "POST"])
@login_required
def edit_customer(cid):
    with get_db() as conn:
        c = row_to_dict(conn.execute("SELECT * FROM customers WHERE id=?", (cid,)).fetchone())
    if not c:
        abort(404)
    if request.method == "POST":
        try:
            name    = request.form.get("name", "").strip()
            email   = request.form.get("email", "").strip()
            phone   = request.form.get("phone", "").strip()
            company = request.form.get("company", "").strip()
            segment = request.form.get("segment", "General").strip()
            notes   = request.form.get("notes", "").strip()
            fvals   = [float(request.form.get(k, 0)) for k in FEATURE_KEYS]

            pred, churn_prob, retain_prob = run_prediction(fvals)
            risk = risk_label(churn_prob)

            cols = ", ".join(f"{k}=?" for k in FEATURE_KEYS)
            with get_db() as conn2:
                conn2.execute(f"""UPDATE customers SET
                    name=?, email=?, phone=?, company=?, segment=?, {cols},
                    prediction=?, churn_probability=?, retain_probability=?,
                    risk_level=?, notes=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?""",
                    [name, email, phone, company, segment, *fvals,
                     pred, churn_prob, retain_prob, risk, notes, cid])
                conn2.execute("""INSERT INTO prediction_history
                    (customer_id,customer_name,customer_email,prediction,
                     churn_probability,retain_probability,risk_level,feature_snapshot)
                    VALUES (?,?,?,?,?,?,?,?)""",
                    [cid, name, email, pred, churn_prob, retain_prob, risk,
                     json.dumps({k: v for k, v in zip(FEATURE_KEYS, fvals)})])

            flash("Customer record updated successfully.", "success")
            return redirect(url_for("result_page", cid=cid))
        except Exception as e:
            flash(f"Update failed: {e}", "error")

    return render_template("edit_customer.html", customer=c, features=FEATURE_CONFIG)

@app.route("/customers/<int:cid>/delete", methods=["POST"])
@login_required
def delete_customer(cid):
    with get_db() as conn:
        conn.execute("DELETE FROM customers WHERE id=?", (cid,))
    flash("Customer record deleted.", "success")
    return redirect(url_for("customers_list"))

@app.route("/history")
@login_required
def history():
    """Customer Prediction History page."""
    page     = int(request.args.get("page", 1))
    per_page = 20
    offset   = (page - 1) * per_page

    with get_db() as conn:
        total_rows = conn.execute("SELECT COUNT(*) FROM prediction_history").fetchone()[0]
        rows = rows_to_list(conn.execute(
            "SELECT * FROM prediction_history ORDER BY triggered_at DESC LIMIT ? OFFSET ?",
            (per_page, offset)).fetchall())

    total_pages = (total_rows + per_page - 1) // per_page
    return render_template("history.html",
        rows=rows, page=page, total_pages=total_pages, total_rows=total_rows)

# ── API Endpoints ─────────────────────────────────────────────────────────────
@app.route("/api/stats")
def api_stats():
    """Dashboard stats for chart rendering."""
    with get_db() as conn:
        customers = rows_to_list(conn.execute("SELECT * FROM customers").fetchall())
        total     = len(customers)
        churned   = sum(1 for c in customers if c["prediction"] == 1)
        retained  = total - churned
        high_risk = sum(1 for c in customers if c.get("risk_level") == "High")
        med_risk  = sum(1 for c in customers if c.get("risk_level") == "Medium")
        low_risk  = sum(1 for c in customers if c.get("risk_level") == "Low")
        avg_churn = (sum(c["churn_probability"] or 0 for c in customers) / total) if total else 0

        seg_rows  = rows_to_list(conn.execute(
            "SELECT segment, COUNT(*) as cnt FROM customers GROUP BY segment").fetchall())

        hist_rows = rows_to_list(conn.execute("""
            SELECT DATE(triggered_at) as day, COUNT(*) as cnt
            FROM prediction_history
            GROUP BY day ORDER BY day DESC LIMIT 14""").fetchall())

    return jsonify({
        "total": total, "churned": churned, "retained": retained,
        "high_risk": high_risk, "med_risk": med_risk, "low_risk": low_risk,
        "avg_churn": round(avg_churn, 1),
        "segments": seg_rows,
        "daily_predictions": list(reversed(hist_rows)),
        "model_ok": _model is not None,
    })

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """Quick JSON-based prediction (for AJAX calls)."""
    data = request.get_json(force=True, silent=True) or {}
    try:
        fvals = [float(data.get(k, 0)) for k in FEATURE_KEYS]
        pred, churn_prob, retain_prob = run_prediction(fvals)
        return jsonify({
            "prediction": pred,
            "churn_probability": churn_prob,
            "retain_probability": retain_prob,
            "risk_level": risk_label(churn_prob),
            "label": "Likely to Churn" if pred == 1 else "Likely to Retain",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/customers")
def api_customers():
    q    = request.args.get("q", "")
    sql  = "SELECT * FROM customers WHERE 1=1"
    args = []
    if q:
        sql += " AND (name LIKE ? OR email LIKE ?)"
        args += [f"%{q}%", f"%{q}%"]
    sql += " ORDER BY updated_at DESC LIMIT 200"
    with get_db() as conn:
        rows = rows_to_list(conn.execute(sql, args).fetchall())
    return jsonify(rows)

@app.route("/api/customers/<int:cid>", methods=["DELETE"])
def api_delete_customer(cid):
    with get_db() as conn:
        conn.execute("DELETE FROM customers WHERE id=?", (cid,))
    return jsonify({"success": True})

# ── Error Handlers ────────────────────────────────────────────────────────────
@app.errorhandler(404)
def err_404(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return render_template("error.html", code=404, message="Page not found"), 404

@app.errorhandler(500)
def err_500(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error"}), 500
    return render_template("error.html", code=500, message="Internal server error"), 500

# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "="*65)
    print("  CartSense – Customer Purchase & Churn Predictor")
    print("="*65)
    print(f"  Model : {PKL_PATH}")
    print(f"  DB    : {DB_PATH}")
    print(f"  Port  : {port}")
    print(f"  URL   : http://localhost:{port}")
    print("="*65 + "\n")
    app.run(debug=True, host="0.0.0.0", port=port)
