from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from tkinter import Tk

import joblib

app = Flask(__name__)

# Configure the database URI (replace 'sqlite:///example.db' with your database URI)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

# Create the main window
master = Tk()
master.withdraw()  # Hide the Tkinter window

# Load the machine learning model
model = joblib.load(r"C:\Users\Kosgei794\Downloads\customer segmentation")

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with app.app_context():  # Create application context
            user = User.query.filter_by(username=username, password=password).first()

        if user:
            return redirect(url_for('index'))  # Redirect to the 'index' route after successful login
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        
        with app.app_context():  # Create application context
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return "Username already exists"
            
            if password != confirm_password:
                return "Passwords do not match"
            
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))  # Redirect to the 'login' route after successful registration
    else:
        return render_template('register.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get input values from the form
        p1 = int(request.form['annual_income'])
        p2 = int(request.form['spending_score'])

        # Perform prediction
        result = model.predict([[p1, p2]])

        if result[0] == 0:
            prediction_text = "Customers with medium annual income and medium annual spend"
        elif result[0] == 1:
            prediction_text = "Customers with high annual income but low annual spend"
        elif result[0] == 2:
            prediction_text = "Customers with low annual income but high annual spend"
        elif result[0] == 3:
            prediction_text = "Customers with high annual income and high annual spend"

        return render_template('index.html', prediction_text=prediction_text)

    except ValueError:
        error_message = "Please enter valid numeric values for Annual Income and Spending Score"
        return render_template('index.html', error_message=error_message)

@app.route('/index')
def index():
    return render_template('index.html')  # Replace 'index.html' with the actual template you want to render

if __name__ == '__main__':
    # Create the database tables before running the app
    with app.app_context():  # Create application context
        db.create_all()
    app.run(debug=True)
