import requests
import time
import psycopg2
from datetime import datetime, timedelta

# Bot configuration
TOKEN = ''  # Bot Token
BASE_URL = f'https://api.telegram.org/bot{TOKEN}'

# Weather API Key
WEATHER_API_KEY = ''

# PostgreSQL setup
conn = psycopg2.connect(
    dbname='test',
    user='root',
    password='root',
    host='localhost',
    port=5432
)
cursor = conn.cursor()

# Get messages from telegram bot
def get_updates(offset=None):
    url = f'{BASE_URL}/getUpdates'
    params = {'timeout': 100, 'offset': offset}
    response = requests.get(url, params=params)
    return response.json()

# Send messages to bot
def send_message(chat_id, text):
    url = f'{BASE_URL}/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=data)

# Get the weather for a specific city at a specific time
def check_weather_logic(city, date_str):
    try:
        requested_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD."

    today = datetime.today().date()
    if requested_date > today + timedelta(days=10):
        return "Forecast is only available for up to 10 days from today."
    if requested_date < today - timedelta(days=10):
        return "Historical data is only available for the past 10 days."

    endpoint = 'history.json' if requested_date < today else 'forecast.json'
    url = f'https://api.weatherapi.com/v1/{endpoint}?key={WEATHER_API_KEY}&q={city}&dt={date_str}'

    try:
        response = requests.get(url)
        data = response.json()
        day_data = data['forecast']['forecastday'][0]['day']
        return (
            f"The weather in {city} on {date_str} had a max temp of {day_data['maxtemp_c']}°C, "
            f"min temp of {day_data['mintemp_c']}°C, and an average of {day_data['avgtemp_c']}°C."
        )
    except Exception:
        return "Failed to retrieve weather data."

# Get user requests history
def get_history_text(user_id, limit=10):
    cursor.execute("""
        SELECT * FROM telegram_logs
        WHERE user_id = %s
        ORDER BY timestamp DESC
        LIMIT %s
    """, (user_id, limit))
    rows = cursor.fetchall()
    history_lines = []
    for row in rows:
        command = row[1]
        generated_request = row[3]
        timestamp = row[4]

        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M")
        history_lines.append(f"Command `{command}` generated `{generated_request}` at {formatted_time}")
    return "\n".join(history_lines) if history_lines else "No history found."

# DB logging
def log_to_db(user_id, command, args, response_text):
    cursor.execute("""
        INSERT INTO telegram_logs (user_id, command, args, response_text, timestamp)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        user_id,
        command,
        ' '.join(args) if args else '',
        response_text,
        datetime.now()
    ))
    conn.commit()

# Main Bot Logic
def main():
    offset = None
    while True:
        updates = get_updates(offset)
        for update in updates.get('result', []):
            message = update.get('message')
            if not message:
                continue

            chat_id = message['chat']['id']
            text = message.get('text', '')
            user_id = message['from'].get('id')
            parts = text.strip().split()

            if not parts:
                send_message(chat_id, "Empty message received.")
                offset = update['update_id'] + 1
                continue

            command = parts[0]
            args = parts[1:]
            generated_request = ''
            response_text = ''

            # --- Handle commands ---
            if command == '/check_weather':
                if len(args) < 2:
                    response_text = "Please provide both city and date. Example: /check_weather London 2025-08-01"
                else:
                    city, date = args[0], args[1]
                    generated_request = f'/check_weather?city={city}&date={date}'
                    response_text = check_weather_logic(city, date)
            elif command == '/history':
                if len(args) < 1:
                    response_text = "Please provide limit number. Example: /history 5"
                else:
                    try:
                        limit = int(args[0])
                        if limit > 10 or limit <= 0:
                            response_text = "Please provide a valid number. The maximum allowed is 10."
                        else:
                            generated_request = '/history'
                            response_text = get_history_text(user_id, limit)
                    except ValueError:
                        response_text = "Invalid number format. Please provide a valid integer limit (max 10)."
            elif command == '/bot_info':
                generated_request = '/bot_info'
                response_text = "This is weather app by DM, version 1.0"
            elif command == '/update_bot':
                generated_request = '/update_bot'
                response_text = "Bot updated"
            else:
                response_text = (
                    "Here are the valid commands you can use:\n\n"
                    "- /check_weather <city> <YYYY-MM-DD> - to get the weather for a specific city at a specific time\n"
                    "- /bot_info - to get information about bot\n"
                    "- /update_bot - to update bot version\n"
                    "- /history <number> - to get history of requests"
                )

            send_message(chat_id, response_text)
            log_to_db(user_id, command, args, response_text)
            offset = update['update_id'] + 1

        time.sleep(1)

if __name__ == '__main__':
    main()