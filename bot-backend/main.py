from flask import Flask, request, jsonify, redirect, url_for, session
import uuid
import secrets
from model import handle_query, faq_data, get_current_timestamp
from database import users_collection, chat_collection, r
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)


@app.route('/')
def index():
    routes = {
        "Register": "/register",
        "Login": "/login/<username>/<password>",
        "Chat": "/chat"
    }
    return jsonify({"message": "Welcome to the Amazon Chatbot!", "available_routes": routes}), 200

@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.json.get('username')
        if not username:
            return jsonify({'error': "No username provided"}), 400
        
        password = request.json.get('password')
        if not password:
            return jsonify({'error': "No password provided"}), 400

        if users_collection.find_one({"username": username}):
            return jsonify({"error": "User already exists. Please log in."}), 400

        users_collection.insert_one({
            "username": username,
            "password": password,
        })
        return jsonify({"message": "Registration successful. Please log in."}), 201
    
    except Exception as e:
        return jsonify({"error": "Unexpected error", "details": str(e)}), 500

@app.route('/login/<username>/<password>', methods=['GET'])
def login(username, password):
    user = users_collection.find_one({"username": username, "password": password})

    if not user:
        return jsonify({"error": "Invalid username or password."}), 401

    session['username'] = username
    session['chat_id'] = str(uuid.uuid4())
    
    r.delete(f"chat:{username}:{session['chat_id']}")  # Ensure no leftover data

    return redirect(url_for('chat'))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return jsonify({"error": "Please log in first."}), 401

    username = session['username']
    chat_id = session['chat_id']

    if request.method == 'POST':
        user_query = request.json.get('message').lower()
        
        if user_query == "logout":
            return redirect(url_for('logout'))

        response = handle_query(user_query, username)
        
        timestamp = get_current_timestamp()
        chat_key = f"chat:{username}:{chat_id}"
        r.rpush(chat_key, f"{timestamp}:user_message:{user_query}")
        r.rpush(chat_key, f"{timestamp}:response:{response}")

        return jsonify({"response": response}), 200

    welcome_message = f"Welcome, {username}! I'm the Amazon Chatbot. How can I assist you today?"
    insights = {
        "FAQ": [faq.question for faq in faq_data.responses],
        "commands": ["logout"]
    }
    return jsonify({"message": welcome_message, "insights": insights}), 200


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if 'username' not in session:
        return jsonify({"error": "You are not logged in."}), 401

    username = session['username']
    chat_id = session['chat_id']
    
    chat_key = f"chat:{username}:{chat_id}"
    chat_history = r.lrange(chat_key, 0, -1)

    if chat_history:
        chat_history_list = []
        for i in range(0, len(chat_history), 2):
            timestamp_user = chat_history[i]
            timestamp_response = chat_history[i + 1]
            user_message = timestamp_user.split(":user_message:")[1]
            response = timestamp_response.split(":response:")[1]
            chat_history_list.append({
                "timestamp": timestamp_user.split(":")[0],
                "query": user_message,
                "response": response
            })

        chat_session = {
            "chat_id": chat_id,
            "timestamp": chat_history_list[0]["timestamp"],
            "messages": chat_history_list
        }

        existing_chat = chat_collection.find_one({"username": username})

        if existing_chat:
            chat_collection.update_one(
                {"username": username},
                {"$push": {"chathistory": chat_session}}
            )
        else:
            chat_collection.insert_one({
                "username": username,
                "chathistory": [chat_session]
            })

    r.delete(chat_key)
    session.pop('username', None)
    session.pop('chat_id', None)

    return jsonify({"message": "You have been logged out successfully."}), 200

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'

    app.run(host=host, port=port, debug=debug)