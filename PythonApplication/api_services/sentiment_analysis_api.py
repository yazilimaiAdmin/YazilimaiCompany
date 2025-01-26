from flask import Flask, request, jsonify
import pyodbc
from textblob import TextBlob

app = Flask(__name__)

def fetch_chat_messages(conversation_id):
    """
    Fetch recent chat messages for a given conversation ID from a SQL Server database.
    
    :param conversation_id: ID of the conversation to fetch messages for.
    :return: List of message contents.
    """
    connection_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=<YOUR_SERVER.database.windows.net,1433;"
        "Database=<YOUR_DATABASE>;"
        "Uid=<YOUR_USER>;"
        "Pwd=<YOUR_PASSWORD>;"
    )
    
    query = """
        SELECT [Content]
        FROM dbo.ChatMessages
        WHERE ConversationId = ?
    """
    
    with pyodbc.connect(connection_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (conversation_id,))
            rows = cursor.fetchall()

    messages = [row[0] for row in rows]
    return messages

def analyze_sentiment(messages):
    """
    Compute the average sentiment of a list of messages using TextBlob.
    
    :param messages: List of message contents.
    :return: Average sentiment score.
    """
    polarity_sum = 0
    count = 0
    for content in messages:
        blob = TextBlob(content)
        polarity_sum += blob.sentiment.polarity  # -1 (negative) to +1 (positive)
        count += 1
    
    if count == 0:
        return 0  # no messages found
    
    average_polarity = polarity_sum / count
    return average_polarity

@app.route('/analyze-sentiment', methods=['POST'])
def analyze_sentiment_route():
    """
    API endpoint to analyze sentiment of recent chat messages for a given conversation ID.
    
    :return: JSON response with average sentiment score.
    """
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    try:
        messages = fetch_chat_messages(conversation_id)
        sentiment_score = analyze_sentiment(messages)
        return jsonify({"average_sentiment_score": sentiment_score}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

