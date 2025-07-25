from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "API is running!"

@app.route('/api/check_weather', methods=['GET'])
def check_weather():
    weather_data = {
        "status": "success",
        "text" : "It is sunny today"
    }
    return jsonify(weather_data), 200

@app.route('/api/history', methods=['GET'])
def history():
    history_data = {
        "status": "success",
        "text" : "today 10pm"
    }
    return jsonify(history_data), 200

@app.route('/api/update_bot', methods=['GET'])
def update_bot():
    update_data = {
        "status": "success",
        "text" : "Bot updated"
    }
    return jsonify(update_data), 200

@app.route('/api/bot_info', methods=['GET'])
def bot_info():
    bot_info_data = {
        "status": "success",
        "text" : "This is weather app by DM, version 1.0"
    }
    return jsonify(bot_info_data), 200

@app.route('/api/<path:any_path>', methods=['GET'])
def catch_all(any_path):
    bot_info_data = {
        "status": "success",
        "text": "Here are the valid commands you can use:\n\n- /check_weather — Get the latest weather updates for your location or any city you specify.\n- /bot_info — Learn more about this bot, including its features and capabilities.\n- /update_bot — Initiate an update to ensure the bot is running with the latest improvements and fixes.\n- /history — View your past interactions and command usage with the bot for easy reference."
    }
    return jsonify(bot_info_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)