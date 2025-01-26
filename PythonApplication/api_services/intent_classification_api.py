import spacy
import pyodbc
from flask import Flask, request, jsonify

# Build and train the intent classifier
def build_intent_classifier(training_data):
    nlp = spacy.blank("en")
    textcat = nlp.add_pipe("textcat", config={"exclusive_classes": True, "architecture": "simple_cnn"})
    
    # Add intent labels
    for _, label in training_data:
        textcat.add_label(label)
    
    # Training loop
    optimizer = nlp.begin_training()
    for epoch in range(10):  # Adjust epochs as needed
        for text, label in training_data:
            doc = nlp.make_doc(text)
            example = spacy.training.Example.from_dict(doc, {"cats": {label: 1.0}})
            nlp.update([example], sgd=optimizer)
    
    # Save the model
    nlp.to_disk("intent_model")
    print("Model training complete and saved!")

# Classify a message's intent
def classify_message_intent(message_text):
    nlp = spacy.load("intent_model")
    doc = nlp(message_text)
    scores = doc.cats
    predicted_intent = max(scores, key=scores.get)
    return predicted_intent

# Store the intent result in the database
def store_intent_result(conversation_id, msg_id, intent):
    connection_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=<YOUR_SERVER.database.windows.net,1433;"
        "Database=<YOUR_DATABASE>;"
        "Uid=<YOUR_USER>;"
        "Pwd=<YOUR_PASSWORD>;"
    )
    query = """
        UPDATE dbo.ChatMessages
        SET Intent = ?
        WHERE ConversationId = ? AND Id = ?
    """
    with pyodbc.connect(connection_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (intent, conversation_id, msg_id))
            conn.commit()
    print("Intent stored successfully!")

# Flask application
app = Flask(__name__)

@app.route('/classify_intent', methods=['POST'])
def classify_intent():
    try:
        data = request.get_json()
        conversation_id = data.get("conversation_id")
        msg_id = data.get("msg_id")
        message_text = data.get("text")
        
        if not all([conversation_id, msg_id, message_text]):
            return jsonify({"error": "Invalid input"}), 400
        
        # Predict intent
        intent = classify_message_intent(message_text)
        
        # Store intent in the database
        store_intent_result(conversation_id, msg_id, intent)
        
        return jsonify({"conversation_id": conversation_id, "msg_id": msg_id, "intent": intent}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Training example (only needed once)
    training_data = [
        ("How much does this cost?", "PRICING_NEGOTIATION"),
        ("I need help with my account.", "TECH_SUPPORT"),
        ("Can I speak to sales?", "SALES_INQUIRY"),
    ]
    build_intent_classifier(training_data)  # Train and save the model
    
    app.run(host='0.0.0.0', port=5000, debug=True)



    """
This Python script provides a complete solution for classifying user messages into specific intents 
(such as "Sales Inquiry," "Technical Support," or "Pricing Negotiation"), storing the classification 
results in an SQL Server database, and exposing this functionality through a Flask API.

Key Components of the Script:

1. Intent Classification with spaCy:
   The build_intent_classifier function creates and trains a text categorization model using spaCy.
   The model assigns probabilities to predefined intent categories based on the input text.
   After training, the model is saved locally as intent_model for future use.

2. Message Classification:
   The classify_message_intent function loads the trained spaCy model and classifies a given message.
   It predicts the most likely intent for the input message by analyzing the text content.

3. Database Integration:
   The store_intent_result function connects to an SQL Server database using the pyodbc library.
   It updates the ChatMessages table with the predicted intent for a specific message, identified by 
   conversation_id and msg_id.

4. Flask API:
   The Flask web server exposes an endpoint /classify_intent to classify user messages in real time.
   Input data (conversation ID, message ID, and message text) is sent to the API via a POST request in JSON format.
   The API predicts the intent, stores it in the database, and returns the result as a JSON response.

Workflow:

1. Model Training:
   Training data is provided as a list of tuples (text, label) in the build_intent_classifier function.
   The model is trained only once and saved locally for future use.

2. Real-Time Classification:
   The /classify_intent API endpoint accepts user input and classifies the intent of the message.
   Once classified, the result is stored in the database and returned to the client.

3. Database Integration:
   The SQL Server database stores the classification result, enabling analytics and tracking of user queries.

How to Use:

1. Install Required Libraries:
   Ensure you have the necessary Python libraries installed, such as Flask, spacy, and pyodbc.
   You can install them via pip:
     pip install flask spacy pyodbc

2. Train the Model:
   Run the script for the first time to train the intent classifier.
   After the model is saved, you can comment out the build_intent_classifier function call to skip retraining.

3. Run the Flask Server:
   Start the Flask server by running the script:
     python app.py
   The server will run on http://localhost:5000 by default.

4. Test the API:
   Use a tool like Postman or cURL to send a POST request to /classify_intent with the following JSON payload:
     {
         "conversation_id": 123,
         "msg_id": 456,
         "text": "I need help with pricing information."
     }
   The API will respond with the predicted intent and store the result in the database.

Important Notes:

1. Security:
   Avoid hardcoding sensitive information like database credentials. Use environment variables or secure key management practices.

2. Performance:
   The current training process uses a basic spaCy pipeline. For large-scale or high-performance systems, consider using a pre-trained language model or cloud-based NLP services.

3. Scalability:
   For better scalability, the API can be deployed using a web server like Gunicorn, and the model can be containerized using Docker.

This script is designed to be modular and extendable, allowing you to add new features, such as:
- Supporting additional intent labels.
- Enhancing the database schema to store advanced analytics.
- Integrating state-of-the-art machine learning models for improved accuracy.
"""
