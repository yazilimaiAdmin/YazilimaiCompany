
from flask import Flask, request, jsonify
import pyodbc
import torch
from transformers import pipeline

app = Flask(__name__)

def summarize_conversation(conversation_id):
    """
    1) Fetch messages from ChatMessages for the given conversation_id.
    2) Concatenate them into a single text block.
    3) Use a transformer-based summarization model (e.g., 'facebook/bart-large-cnn')
       to generate a concise summary.
    """
    connection_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=<YOUR_SERVER.database.windows.net,1433;"
        "Database=<YOUR_DATABASE>;"
        "Uid=<YOUR_USER>;"
        "Pwd=<YOUR_PASSWORD>;"
    )

    fetch_query = """
        SELECT [Content]
        FROM dbo.ChatMessages
        WHERE ConversationId = ?
        ORDER BY [Timestamp]
    """
    
    with pyodbc.connect(connection_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute(fetch_query, (conversation_id,))
            rows = cursor.fetchall()

    # Combine all messages into a single string
    conversation_text = "\n".join(row[0] for row in rows if row[0])

    # Use a pre-trained summarization model
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary_list = summarizer(conversation_text, max_length=130, min_length=30, do_sample=False)
    summary_text = summary_list[0]['summary_text']

    return summary_text

@app.route('/summarize-conversation', methods=['POST'])
def summarize_conversation_route():
    """
    API endpoint to summarize a conversation based on the conversation_id.
    
    :return: JSON response containing the summary text.
    """
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    try:
        summary = summarize_conversation(conversation_id)
        return jsonify({"summary_text": summary}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
