from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from private_gpt_api import PrivateGPTQueryInterface, Config

import json
from json import JSONEncoder, dumps


# Define a custom JSONEncoder
class CustomEncoder(JSONEncoder):
    def default(self, obj):
        # Convert Document object (or any other custom object) to dictionary
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)


app = Flask(__name__)
conf = Config()
private_gpt_query_interface = PrivateGPTQueryInterface(conf)

# Initialize SocketIO with the Flask app
socketio = SocketIO(app, cors_allowed_origins="*")  # cors_allowed_origins for handling CORS issues if any


# Deprecated HTTP POST version, you can remove if you want
@app.route('/ask', methods=['POST'])
def ask():
    query = request.json.get('query', '')
    response = private_gpt_query_interface.get_answer(query)
    return jsonify(response)


@socketio.on('send_message')
def handle_message(message):
    # First, attempt to load the message as JSON
    try:
        data = json.loads(message)
        query = data['query']
    except (json.JSONDecodeError, TypeError, KeyError):
        # If there's an error decoding or the expected key isn't there, handle it
        print("Error processing message:", message)
        return
    print(query)
    response = private_gpt_query_interface.get_answer(query)

    # Convert the response to a JSON string using the custom encoder
    serialized_response = dumps(response, cls=CustomEncoder)
    emit('receive_response', serialized_response)

# @socketio.on('send_message')
# def handle_message(message):
#     try:
#         data = json.loads(message)
#         query = data['query']
#     except (json.JSONDecodeError, TypeError, KeyError):
#         print("Error processing message:", message)
#         return
#
#     def emit_chunk(chunk):
#         serialized_chunk = dumps(chunk, cls=CustomEncoder)  # Assuming you're using a custom encoder
#         emit('receive_response', serialized_chunk)
#
#     private_gpt_query_interface.get_answer_in_chunks(query, emit_chunk)


@socketio.on('connect')
def handle_connection():
    print('Client connected')
    emit('status', {'data': 'Connected'})


@socketio.on('disconnect')
def handle_disconnection():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
