from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime

app = Flask(__name__)

def log_ai_response(conversation_id, content):
    """
    Insert a new AI-generated message into the ChatMessages table.
    
    :param conversation_id: ID of the conversation.
    :param content: The content of the AI-generated message.
    :return: None
    """
    connection_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=<YOUR_SERVER.database.windows.net,1433;"
        "Database=<YOUR_DATABASE>;"
        "Uid=<YOUR_USER>;"
        "Pwd=<YOUR_PASSWORD>;"
    )
    
    query = """
        INSERT INTO dbo.ChatMessages
            (ConversationId, UserId, [Content], Role, [Timestamp])
        VALUES (?, ?, ?, ?, ?)
    """
    
    now = datetime.utcnow()
    
    with pyodbc.connect(connection_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (
                conversation_id,
                "AI_ASSISTANT",  # or None
                content,
                "assistant",
                now
            ))
            conn.commit()

@app.route('/log-ai-response', methods=['POST'])
def log_ai_response_route():
    """
    API endpoint to log AI-generated messages into the ChatMessages table.
    
    :return: JSON response indicating success or error.
    """
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    content = data.get('content')
    try:
        log_ai_response(conversation_id, content)
        return jsonify({"message": "AI response logged successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

