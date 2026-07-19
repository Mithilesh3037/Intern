# 🎯 CartSense - Customer Purchase & Churn Predictor

A professional Flask web application that uses Machine Learning to predict customer purchase behavior and churn probability. Built with Python, Flask, HTML5, CSS3, JavaScript, SQLite, and Scikit-learn.

---

## 📋 Table of Contents

1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Installation & Setup](#installation--setup)
4. [Running the Application](#running-the-application)
5. [How to Use](#how-to-use)
6. [API Documentation](#api-documentation)
7. [Database Schema](#database-schema)
8. [Deployment to Render](#deployment-to-render)
9. [Troubleshooting](#troubleshooting)
10. [Future Enhancements](#future-enhancements)

---

## ✨ Features

### 🤖 Machine Learning
- **Trained ML Model**: Uses a pre-trained LogisticRegression model from scikit-learn
- **Churn Prediction**: Predicts whether a customer will make a repeat purchase
- **Confidence Scores**: Provides prediction confidence percentage (0-100%)
- **Real-time Predictions**: Instant predictions using the loaded model

### 📊 Customer Management
- **Add Customers**: Enter customer details through a professional form
- **View All Records**: See all customer predictions in a dashboard
- **Search Customers**: Filter customers by name or email
- **Edit Customer Data**: Update existing customer information
- **Delete Records**: Remove customer records from the database

### 💾 Data Persistence
- **SQLite Database**: Stores all customer data and predictions
- **Automatic Logging**: All predictions are automatically saved

### 🎨 User Interface
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Professional UI**: Clean, modern interface with Bootstrap
- **Form Validation**: Client-side and server-side validation
- **Real-time Feedback**: Alerts and notifications for user actions

### 🔒 Error Handling
- **Graceful Error Handling**: User-friendly error messages
- **Input Validation**: Comprehensive validation on all inputs
- **Email Uniqueness**: Prevents duplicate customer emails

---

## 📁 Project Structure

```
cartsense_project/
│
├── app.py                          # Main Flask application (Backend)
├── requirements.txt                # Python dependencies
├── customers.db                    # SQLite database (created automatically)
│
├── templates/                      # HTML Templates
│   ├── base.html                  # Base template (navigation, footer)
│   ├── index.html                 # Home page with prediction form
│   ├── dashboard.html             # Customer records dashboard
│   └── error.html                 # Error page
│
├── static/                         # Static files
│   ├── css/
│   │   └── style.css              # Professional CSS styling
│   └── js/
│       └── main.js                # JavaScript utilities and functions
│
└── README.md                       # This file
```

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.8 or higher**: [Download here](https://www.python.org/downloads/)
- **Git** (optional): For cloning/version control
- **pip**: Python package installer (comes with Python)

### Step 1: Create a Virtual Environment (Recommended)

```bash
# Navigate to your project directory
cd cartsense_project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

**What gets installed:**
- `Flask` - Web framework
- `scikit-learn` - Machine Learning library
- `numpy` - Numerical computing
- `pandas` - Data handling
- `gunicorn` - Production server
- And other supporting libraries

### Step 3: Verify Installation

```bash
# Check Flask installation
python -c "import flask; print(flask.__version__)"

# Check scikit-learn installation
python -c "import sklearn; print(sklearn.__version__)"

# Check if model file exists
python -c "import os; print('Model exists!' if os.path.exists('logistic_regression_spam_detector.pkl') else 'Model NOT found!')"
```

---

## ▶️ Running the Application

### Local Development Server

```bash
# Make sure you're in the cartsense_project directory
cd cartsense_project

# Activate virtual environment (if not already activated)
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Run the Flask app
python app.py
```

**Expected Output:**
```
======================================================================
CartSense - Customer Purchase & Churn Predictor
======================================================================

✓ Model loaded: logistic_regression_spam_detector.pkl
✓ Database: customers.db

🚀 Starting Flask server...
📍 Access the application at: http://localhost:5000

Press Ctrl+C to stop the server
======================================================================
```

### Access the Application

1. **Home Page** (Make Predictions):
   ```
   http://localhost:5000/
   ```

2. **Dashboard** (View Records):
   ```
   http://localhost:5000/dashboard
   ```

---

## 💡 How to Use

### Making a Prediction

1. **Go to Home Page**: Navigate to `http://localhost:5000/`

2. **Fill the Form**: Enter customer details:
   - **Personal Information**: Name, Email, Age
   - **Account Information**: Tenure, Contract Length, Internet Service
   - **Financial Information**: Monthly Charges, Total Charges
   - **Purchase Behavior**: Number of Products, Purchase Frequency, Average Order Value
   - **Support**: Customer Support Calls

3. **Click "Predict Now"**: Submit the form

4. **View Result**: 
   - See the prediction (YES/NO)
   - Check confidence score (0-100%)
   - Data automatically saved to database

5. **View Record**: 
   - Click "View All Records" to see the saved record in the dashboard

### Managing Customers

#### View All Customers
- Navigate to `/dashboard`
- See all customers in a table with statistics
- Check total customers, will purchase, won't purchase, and average confidence

#### Search Customers
- Use the search box on the dashboard
- Search by name or email
- Results update instantly

#### Edit Customer
1. Click the **Edit** (pencil) icon next to a customer
2. Update the information in the modal
3. Click "Save Changes"
4. Prediction is automatically recalculated

#### Delete Customer
1. Click the **Delete** (trash) icon next to a customer
2. Confirm the deletion
3. Record is permanently removed from the database

---

## 📚 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### 1. Make a Prediction
```http
POST /api/predict
Content-Type: application/json

Request Body:
{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 35,
    "tenure_months": 24,
    "monthly_charges": 85.50,
    "total_charges": 2045.00,
    "contract_length": 12,
    "internet_service": 1,
    "num_products": 3,
    "customer_support_calls": 2,
    "purchase_frequency": 4.5,
    "avg_order_value": 125.75
}

Response:
{
    "success": true,
    "customer_id": 1,
    "prediction": 1,
    "confidence": 85.32,
    "message": "YES - Customer will make repeat purchase",
    "timestamp": "2024-01-15 10:30:45"
}
```

#### 2. Get All Customers
```http
GET /api/customers

Response:
[
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "age": 35,
        "prediction": 1,
        "prediction_confidence": 85.32,
        "created_at": "2024-01-15 10:30:45",
        ...more fields...
    }
]
```

#### 3. Get Specific Customer
```http
GET /api/customers/{id}

Response:
{
    "id": 1,
    "name": "John Doe",
    ...
}
```

#### 4. Update Customer
```http
PUT /api/customers/{id}
Content-Type: application/json

Request Body: (same as POST /api/predict)

Response:
{
    "success": true,
    "message": "Customer updated successfully"
}
```

#### 5. Delete Customer
```http
DELETE /api/customers/{id}

Response:
{
    "success": true,
    "message": "Customer deleted successfully"
}
```

#### 6. Search Customers
```http
GET /api/search?query=John

Response: (array of matching customers)
[
    {
        "id": 1,
        "name": "John Doe",
        ...
    }
]
```

---

## 🗄️ Database Schema

### Table: `customers`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER (PK) | Unique customer identifier |
| `name` | TEXT | Customer's full name |
| `email` | TEXT (UNIQUE) | Customer's email address |
| `age` | INTEGER | Customer's age in years |
| `tenure_months` | INTEGER | Months as customer |
| `monthly_charges` | REAL | Monthly spending amount |
| `total_charges` | REAL | Total lifetime spending |
| `contract_length` | INTEGER | Contract duration in months |
| `internet_service` | INTEGER | 0 = No, 1 = Yes |
| `num_products` | INTEGER | Number of products purchased |
| `customer_support_calls` | INTEGER | Times contacted support |
| `purchase_frequency` | REAL | Purchases per month |
| `avg_order_value` | REAL | Average purchase amount |
| `prediction` | INTEGER | Model prediction (0 or 1) |
| `prediction_confidence` | REAL | Confidence percentage (0-100) |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |

---

## 🌐 Deployment to Render

### Prerequisites
- GitHub account with the code pushed
- Render account (free tier available)

### Step-by-Step Deployment

#### 1. Create GitHub Repository
```bash
# Initialize git (if not already done)
git init

# Add files to git
git add .
git commit -m "Initial commit: CartSense project"

# Push to GitHub
git remote add origin https://github.com/yourusername/cartsense.git
git branch -M main
git push -u origin main
```

#### 2. Create Render Account
- Go to [render.com](https://render.com)
- Sign up with GitHub
- Authorize Render to access your repositories

#### 3. Create New Web Service
1. Click "New +" button
2. Select "Web Service"
3. Connect your GitHub repository
4. Fill in details:
   - **Name**: cartsense
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

#### 4. Add Environment Variables (if needed)
- In Render dashboard, go to your service settings
- Add environment variables:
  ```
  FLASK_ENV=production
  FLASK_DEBUG=False
  ```

#### 5. Deploy
- Click "Deploy"
- Wait for build to complete
- Application will be live at: `https://cartsense-xxxx.onrender.com`

#### 6. Verify Deployment
- Visit your deployment URL
- Test prediction functionality
- Check if database is being created

---

## 🔧 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'flask'`
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Port 5000 already in use
**Solution:**
```bash
python app.py  # Will automatically use a different port
# Or specify a different port:
# Edit app.py and change: app.run(port=5001)
```

### Issue: Model file not found
**Solution:**
- Ensure `logistic_regression_spam_detector.pkl` is in the project root
- Check that the file is not corrupted
- Run: `python analyze_model.py` to verify model

### Issue: Database locked
**Solution:**
```bash
# Close any open connections to customers.db
# Delete customers.db (it will be recreated)
rm customers.db
# Restart the application
python app.py
```

### Issue: 404 error on templates
**Solution:**
- Verify the `templates` folder exists
- Check that all .html files are in the templates folder
- Restart the Flask server

### Issue: Predictions not saving
**Solution:**
1. Check that email addresses are unique
2. Verify database permissions
3. Check Flask console for error messages
4. Restart the application

---

## 🎓 Understanding the Code

### app.py Structure

**Sections:**
1. **Imports** - All required libraries
2. **Flask Initialization** - App setup
3. **Model Loading** - Load .pkl file
4. **Database Setup** - Initialize SQLite
5. **Helper Functions** - Utilities
6. **Input Validation** - Validate user data
7. **Prediction Functions** - Make predictions
8. **Page Routes** - Render HTML pages
9. **API Routes** - JSON responses
10. **CRUD Operations** - Create, Read, Update, Delete
11. **Search** - Search functionality
12. **Error Handlers** - Handle errors gracefully

### Key Concepts

**Model Loading:**
```python
model = pickle.load(open('model.pkl', 'rb'))
```

**Making Predictions:**
```python
prediction = model.predict([features])[0]
confidence = model.predict_proba([features])[0]
```

**Database Operations:**
```python
conn = sqlite3.connect('customers.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM customers')
```

---

## 📈 Performance Tips

1. **Database Indexing**:
   - Add index on frequently searched columns (email, name)

2. **Caching**:
   - Cache model predictions for identical inputs

3. **Batch Processing**:
   - Process multiple predictions in batch mode

4. **Optimize Model**:
   - Consider model compression for faster loading

---

## 🔐 Security Considerations

1. **Email Validation**: Unique email constraint prevents duplicates
2. **Input Sanitization**: All inputs are validated
3. **SQL Injection Protection**: Using parameterized queries
4. **CORS**: Enabled for cross-origin requests
5. **Error Messages**: Generic messages (don't expose sensitive info)

---

## 🚀 Future Enhancements

1. **User Authentication**:
   - Add user login/signup
   - Role-based access control

2. **Advanced Analytics**:
   - Charts and graphs
   - Prediction trends
   - Customer segmentation

3. **Export Features**:
   - Download predictions as CSV/Excel
   - Generate PDF reports

4. **API Key Support**:
   - For external integrations
   - Rate limiting

5. **Batch Predictions**:
   - Upload CSV file for bulk predictions
   - Asynchronous job processing

6. **Model Retraining**:
   - Upload new model file
   - A/B testing between models

---

## 📞 Support & Contact

For issues, questions, or suggestions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review code comments in app.py
3. Check Flask documentation: https://flask.palletsprojects.com

---

## 📄 License

This project is provided for educational and internship purposes.

---

## ✅ Checklist Before Submission

- [ ] All features working correctly
- [ ] Database saves predictions
- [ ] Search/Edit/Delete functions work
- [ ] Form validation working
- [ ] Responsive design tested on mobile
- [ ] No console errors in browser
- [ ] No Flask errors in terminal
- [ ] README.md complete and clear
- [ ] Code is well-commented
- [ ] requirements.txt updated

---

## 🎉 Congratulations!

You now have a fully functional Machine Learning web application ready for production! 

**Next Steps:**
1. Test thoroughly
2. Deploy to Render
3. Share with stakeholders
4. Gather feedback
5. Iterate and improve

Good luck with your internship project! 🚀

---

*Last Updated: January 2024*
*CartSense v1.0.0*
