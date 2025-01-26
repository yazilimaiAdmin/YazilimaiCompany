from flask import Flask, request, jsonify
import pyodbc
import pandas as pd
from sklearn.linear_model import LinearRegression
from joblib import dump, load

app = Flask(__name__)

def train_pricing_model():
    """
    1) Load data from dbo.Pricing or any historical table that includes
       features (e.g., project complexity, time, existing min/max price).
    2) Train a regression model to predict a refined price range.
    3) Save the model for inference.
    """
    connection_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=<YOUR_SERVER.database.windows.net,1433;"
        "Database=<YOUR_DATABASE>;"
        "Uid=<YOUR_USER>;"
        "Pwd=<YOUR_PASSWORD>;"
    )

    fetch_query = """
        SELECT
            PriceInLiraMin,
            PriceInLiraMaxTL,
            ProjectTime,
            ServicePackage
        FROM dbo.Pricing
    """

    with pyodbc.connect(connection_str) as conn:
        df = pd.read_sql(fetch_query, conn)

    # Simplified example: let's assume "PriceInLiraMaxTL" is the target to predict
    features = ["ProjectTime"]  # Add more if available
    X = df[features]
    y = df["PriceInLiraMaxTL"]
    
    model = LinearRegression()
    model.fit(X, y)

    # Save the model locally or to a blob storage
    dump(model, "pricing_model.joblib")
    print("Pricing model trained and saved successfully.")

def predict_optimal_price(project_time):
    """
    Load the trained model, then predict the suggested max price.
    """
    model = load("pricing_model.joblib")
    predicted_max = model.predict([[project_time]])[0]
    return predicted_max

@app.route('/train-pricing-model', methods=['POST'])
def train_pricing_model_route():
    """
    API endpoint to train the pricing model.
    
    :return: JSON response indicating success or error.
    """
    try:
        train_pricing_model()
        return jsonify({"message": "Pricing model trained and saved successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict-price', methods=['POST'])
def predict_price_route():
    """
    API endpoint to predict the optimal price based on project time.
    
    :return: JSON response containing the predicted price.
    """
    data = request.get_json()
    project_time = data.get('project_time')
    try:
        predicted_price = predict_optimal_price(project_time)
        return jsonify({"predicted_price": predicted_price}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
