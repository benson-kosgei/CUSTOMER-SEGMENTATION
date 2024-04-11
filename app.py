from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import joblib
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

app = Flask(__name__)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

# Load the machine learning model
model_path = r"C:\Users\Kosgei794\Downloads\kmeans_model (3).joblib"  # Ensure this path is correct
model = joblib.load(model_path)

# Dummy data for demonstration purposes (Replace with your actual data)
X = np.random.rand(100, 2) * 100  # Dummy feature data
y_means = np.random.randint(0, 4, size=100)  # Dummy cluster assignments

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists"

        if password != confirm_password:
            return "Passwords do not match"

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        p1 = int(request.form['annual_income'])
        p2 = int(request.form['spending_score'])
        result = model.predict(np.array([[p1, p2]]))

        # Define prediction text based on cluster result
        cluster_names = {
            0: "CUSTOMERS WITH MEDIUM ANNUAL INCOME AND MEDIUM ANNUAL SPEND (CLUSTER 0)",
            1: "CUSTOMERS WITH HIGH ANNUAL INCOME BUT LOW ANNUAL SPEND (CLUSTER 1)",
            2: "CUSTOMERS WITH LOW ANNUAL INCOME BUT HIGH ANNUAL SPEND (CLUSTER 2)",
            3: "CUSTOMERS WITH HIGH ANNUAL INCOME AND HIGH ANNUAL SPEND (CLUSTER 3)"
        }
        prediction_text = cluster_names.get(result[0], "Unknown Cluster")

        # Plot generation
        plt.figure(figsize=(6, 4))
        for i in range(4):  # Assuming 4 clusters for demonstration
            plt.scatter(X[y_means == i, 0], X[y_means == i, 1], label=f'Cluster {i}')
        plt.scatter(p1, p2, color='red', marker='o', label='New Data Point')  # Mark the new data point
        plt.xlabel('Annual Income')
        plt.ylabel('Spending Score')
        plt.legend()
        plt.title('Customer Segmentation')

        # Convert plot to PNG image and then to base64 (string) to embed in HTML
        pic_IObytes = io.BytesIO()
        plt.savefig(pic_IObytes, format='png')
        pic_IObytes.seek(0)
        plot_url = base64.b64encode(pic_IObytes.read()).decode()

        return render_template('index.html', prediction_text=prediction_text, plot_url=plot_url)
    except ValueError:
        return render_template('index.html', error_message="Please enter valid numeric values for Annual Income and Spending Score")

@app.route('/index')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():  # Set up application context
        db.create_all()  # Create database tables
    app.run(debug=True)
