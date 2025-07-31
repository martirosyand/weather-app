from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
api_key = "1dd230835dcb4d4ab8f64234253107" 

@app.route('/', methods=['GET'])
def home():
    return "API is running!"

@app.route('/api/check_weather', methods=['GET'])
def check_weather():

    date_str = request.args.get('date')
    city = request.args.get('city')

    requested_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    today = datetime.today().date()
    max_future_date = today + timedelta(days=10)
    max_past_date = today - timedelta(days=7)  # adjust based on your plan

    if requested_date > max_future_date:
        return jsonify({
        "status": "error",
        "text": "Forecast is only available for up to 10 days from today."
        }), 200

    if requested_date < max_past_date:
        return jsonify({
            "status": "error",
            "text": "Historical data is only available for the past 7 days."
        }), 200

    if requested_date < today:
        endpoint = 'history.json'
    else:
        endpoint = 'forecast.json'

    url = f'https://api.weatherapi.com/v1/{endpoint}?key={api_key}&q={city}&dt={date_str}'

    response = requests.get(url)
    data = response.json()
    day_data = data['forecast']['forecastday'][0]['day']
    
    max_temp = day_data['maxtemp_c']
    min_temp = day_data['mintemp_c']
    avg_temp = day_data['avgtemp_c']

    weather_data = {
            "status": "success",
            "text": (
                f"The weather in {city} on {date_str} had a max temp of {max_temp}°C, "
                f"min temp of {min_temp}°C, and an average of {avg_temp}°C."
            )
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