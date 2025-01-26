from flask import Flask, request, jsonify
import pyodbc

app = Flask(__name__)

def suggest_pricing(service_requested):
    """
    Provide pricing suggestions from the Pricing table based on the service requested.
    
    :param service_requested: The service package requested by the user.
    :return: List of matching pricing options.
    """
    connection_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=<YOUR_SERVER.database.windows.net,1433;"
        "Database=<YOUR_DATABASE>;"
        "Uid=<YOUR_USER>;"
        "Pwd=<YOUR_PASSWORD>;"
    )
    
    query = """
        SELECT
            Id,
            ServicePackage,
            Description,
            PriceInLiraMin,
            PriceInLiraMaxTL,
            ProjectTime
        FROM dbo.Pricing
        WHERE ServicePackage LIKE ?
    """
    
    with pyodbc.connect(connection_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, f"%{service_requested}%")
            rows = cursor.fetchall()
    
    # Return all matching rows
    results = []
    for row in rows:
        results.append({
            "Id": row[0],
            "ServicePackage": row[1],
            "Description": row[2],
            "PriceMin": row[3],
            "PriceMax": row[4],
            "ProjectTimeDays": row[5]
        })
    
    return results

@app.route('/suggest-pricing', methods=['POST'])
def suggest_pricing_route():
    """
    API endpoint to suggest pricing options based on the service requested.
    
    :return: JSON response with pricing suggestions.
    """
    data = request.get_json()
    service_requested = data.get('service_requested')
    try:
        pricing_options = suggest_pricing(service_requested)
        return jsonify(pricing_options), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
