import os
import sqlite3
from datetime import datetime

from flask import Flask, flash, g, redirect, render_template, request, url_for
from waitress import serve

app = Flask(__name__)
app.secret_key = "personal-expense-tracker-secret-key"

DATABASE = os.path.join(app.root_path, "expense.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            expense_date TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()


with app.app_context():
    init_db()


@app.route("/")
def index():
    db = get_db()
    total_expenses = db.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses"
    ).fetchone()["total"]
    total_categories = db.execute(
        "SELECT COUNT(DISTINCT category) AS count FROM expenses"
    ).fetchone()["count"]
    current_month = datetime.now().strftime("%Y-%m")
    monthly_expense = db.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE expense_date LIKE ?",
        (f"{current_month}%",),
    ).fetchone()["total"]
    recent_expenses = db.execute(
        "SELECT * FROM expenses ORDER BY created_at DESC LIMIT 5"
    ).fetchall()

    return render_template(
        "index.html",
        total_expenses=total_expenses,
        total_categories=total_categories,
        monthly_expense=monthly_expense,
        recent_expenses=recent_expenses,
    )


@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        amount = request.form.get("amount", "").strip()
        expense_date = request.form.get("expense_date", "").strip()
        description = request.form.get("description", "").strip()

        errors = []
        if not title:
            errors.append("Expense title is required.")
        if not category:
            errors.append("Category is required.")
        if not amount:
            errors.append("Amount is required.")
        if not expense_date:
            errors.append("Expense date is required.")

        try:
            amount_value = float(amount)
            if amount_value <= 0:
                errors.append("Amount must be greater than zero.")
        except ValueError:
            errors.append("Amount must be a valid number.")

        if errors:
            return render_template(
                "add_expense.html",
                errors=errors,
                form={
                    "title": title,
                    "category": category,
                    "amount": amount,
                    "expense_date": expense_date,
                    "description": description,
                },
            )

        db = get_db()
        db.execute(
            """
            INSERT INTO expenses (title, category, amount, expense_date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, category, amount_value, expense_date, description),
        )
        db.commit()
        flash("Expense added successfully!", "success")
        return redirect(url_for("expenses"))

    return render_template("add_expense.html", errors=[], form={})


@app.route("/expenses")
def expenses():
    db = get_db()
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    sort = request.args.get("sort", "desc")

    query = "SELECT * FROM expenses WHERE 1=1"
    params = []

    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")

    if category:
        query += " AND category = ?"
        params.append(category)

    if sort == "asc":
        query += " ORDER BY expense_date ASC"
    else:
        query += " ORDER BY expense_date DESC"

    expenses = db.execute(query, params).fetchall()
    categories = db.execute(
        "SELECT DISTINCT category FROM expenses ORDER BY category"
    ).fetchall()

    return render_template(
        "expenses.html",
        expenses=expenses,
        categories=categories,
        search=search,
        selected_category=category,
        sort=sort,
    )


@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):
    db = get_db()
    expense = db.execute(
        "SELECT * FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()

    if expense is None:
        flash("Expense not found.", "danger")
        return redirect(url_for("expenses"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        amount = request.form.get("amount", "").strip()
        expense_date = request.form.get("expense_date", "").strip()
        description = request.form.get("description", "").strip()

        errors = []
        if not title:
            errors.append("Expense title is required.")
        if not category:
            errors.append("Category is required.")
        if not amount:
            errors.append("Amount is required.")
        if not expense_date:
            errors.append("Expense date is required.")

        try:
            amount_value = float(amount)
            if amount_value <= 0:
                errors.append("Amount must be greater than zero.")
        except ValueError:
            errors.append("Amount must be a valid number.")

        if errors:
            return render_template(
                "edit_expense.html",
                expense=expense,
                errors=errors,
                form={
                    "title": title,
                    "category": category,
                    "amount": amount,
                    "expense_date": expense_date,
                    "description": description,
                },
            )

        db.execute(
            """
            UPDATE expenses
            SET title = ?, category = ?, amount = ?, expense_date = ?, description = ?
            WHERE id = ?
            """,
            (title, category, amount_value, expense_date, description, expense_id),
        )
        db.commit()
        flash("Expense updated successfully!", "success")
        return redirect(url_for("expenses"))

    return render_template("edit_expense.html", expense=expense, errors=[], form={})


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    db = get_db()
    db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    db.commit()
    flash("Expense deleted successfully!", "success")
    return redirect(url_for("expenses"))


@app.route("/summary")
def summary():
    db = get_db()
    total_expenses = db.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses"
    ).fetchone()["total"]
    category_totals = db.execute(
        "SELECT category, COALESCE(SUM(amount), 0) AS total FROM expenses GROUP BY category ORDER BY total DESC"
    ).fetchall()
    highest_expense = db.execute(
        "SELECT * FROM expenses ORDER BY amount DESC LIMIT 1"
    ).fetchone()
    lowest_expense = db.execute(
        "SELECT * FROM expenses ORDER BY amount ASC LIMIT 1"
    ).fetchone()
    current_month = datetime.now().strftime("%Y-%m")
    monthly_total = db.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE expense_date LIKE ?",
        (f"{current_month}%",),
    ).fetchone()["total"]

    return render_template(
        "summary.html",
        total_expenses=total_expenses,
        category_totals=category_totals,
        highest_expense=highest_expense,
        lowest_expense=lowest_expense,
        monthly_total=monthly_total,
    )


if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=5000)
