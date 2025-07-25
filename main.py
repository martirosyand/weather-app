from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "API is running!"

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    print("Received data:", data)
    return jsonify({"status": "success", "received": data}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)