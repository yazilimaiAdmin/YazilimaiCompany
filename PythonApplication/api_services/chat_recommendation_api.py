from flask import Flask, request, jsonify
import pyodbc
import redis
import pandas as pd

app = Flask(__name__)

def load_popular_packages_into_cache():
    """
    Fetch top packages from SQL, store them in Redis for fast retrieval by the AI assistant.
    """
    r = redis.Redis(host="<YOUR_SERVER>.redis.cache.windows.net", port=6380, password="<YOUR_PASSWORD>", ssl=True)

    connection_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=<YOUR_SERVER.database.windows.net,1433;"
        "Database=<YOUR_DATABASE>;"
        "Uid=<YOUR_USER>;"
        "Pwd=<YOUR_PASSWORD>;"
    )
    
    query = """
        SELECT TOP (10)
            ServicePackage, PriceInLiraMin, PriceInLiraMaxTL, ProjectTime
        FROM dbo.Pricing
        ORDER BY PriceInLiraMaxTL DESC
    """

    with pyodbc.connect(connection_str) as conn:
        df_packages = pd.read_sql(query, conn)

    # Convert each row to a dict and store in Redis as a list or hash
    packages_list = df_packages.to_dict("records")
    r.set("popular_packages", str(packages_list))  # simplistic approach; better to store JSON

    return packages_list

def get_popular_packages_from_cache():
    r = redis.Redis(host="<YOUR_SERVER>.redis.cache.windows.net", port=6380, password="<YOUR_PASSWORD>", ssl=True)
    cached_val = r.get("popular_packages")
    if cached_val:
        # Convert from string/JSON back to Python objects
        packages_list = eval(cached_val)  # or parse JSON if stored as JSON
        return packages_list
    else:
        return []

@app.route('/load-popular-packages', methods=['POST'])
def load_popular_packages_route():
    """
    API endpoint to load popular packages into Redis cache.
    
    :return: JSON response indicating the loaded packages.
    """
    try:
        loaded_data = load_popular_packages_into_cache()
        return jsonify({"loaded_packages": loaded_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-popular-packages', methods=['GET'])
def get_popular_packages_route():
    """
    API endpoint to get popular packages from Redis cache.
    
    :return: JSON response containing the cached packages.
    """
    try:
        cached_data = get_popular_packages_from_cache()
        return jsonify({"cached_packages": cached_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
