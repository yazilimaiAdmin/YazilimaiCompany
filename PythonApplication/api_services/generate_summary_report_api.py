from flask import Flask, request, jsonify
import pyodbc
import pandas as pd

app = Flask(__name__)

def generate_summary_report():
    """
    Generate a simple summary report of interactions versus chosen packages.
    
    :return: Dictionary containing summary data.
    """
    connection_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=<YOUR_SERVER.database.windows.net,1433;"
        "Database=<YOUR_DATABASE>;"
        "Uid=<YOUR_USER>;"
        "Pwd=<YOUR_PASSWORD>;"
    )
    
    query_messages = """
        SELECT
            ConversationId,
            COUNT(*) AS MessageCount
        FROM dbo.ChatMessages
        GROUP BY ConversationId
    """
    
    query_pricing_acceptance = """
        SELECT
            COUNT(*) AS AcceptanceCount,
            ServicePackage
        FROM dbo.ChatMessages
        WHERE [Content] LIKE '%Service Package Accepted%'
        GROUP BY ServicePackage
    """
    
    with pyodbc.connect(connection_str) as conn:
        df_messages = pd.read_sql(query_messages, conn)
        df_pricing_acceptance = pd.read_sql(query_pricing_acceptance, conn)
    
    # Example summary:
    total_conversations = df_messages['ConversationId'].nunique()
    total_messages = df_messages['MessageCount'].sum()
    
    summary = {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "package_acceptance_overview": df_pricing_acceptance.to_dict(orient='records')
    }
    
    return summary

@app.route('/generate-summary-report', methods=['GET'])
def generate_summary_report_route():
    """
    API endpoint to generate a summary report of interactions versus chosen packages.
    
    :return: JSON response containing summary data.
    """
    try:
        summary = generate_summary_report()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
