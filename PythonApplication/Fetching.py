from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime

app = Flask(__name__)

def fetch_chat_messages(conversation_id, limit=20):
    connection_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=<YOUR_SERVER.database.windows.net,1433;"
        "Database=<YOUR_DATABASE>;"
        "Uid=<YOUR_USER>;"
        "Pwd=<YOUR_PASSWORD>;"
    )
    
    query = f"""
        SELECT TOP({limit})
            Id,
            UserId,
            [Content],
            Role,
            [Timestamp]
        FROM dbo.ChatMessages
        WHERE ConversationId = ?
        ORDER BY [Timestamp] DESC
    """
    
    with pyodbc.connect(connection_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (conversation_id,))
            rows = cursor.fetchall()
    
    messages = []
    for row in rows:
        messages.append({
            "Id": row[0],
            "UserId": row[1],
            "Content": row[2],
            "Role": row[3],
            "Timestamp": row[4].strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return messages

@app.route('/get-messages', methods=['POST'])
def get_messages():
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    limit = data.get('limit', 20)  # default limit is 20

    try:
        messages = fetch_chat_messages(conversation_id, limit)
        return jsonify(messages), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
