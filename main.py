from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
import psycopg2
from datetime import datetime, timedelta
import requests

# Bot configuration
TOKEN = ''  # Bot Token
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

def is_user_authorized(username):
    cursor.execute("SELECT * FROM telegram_users WHERE username = %s", (username,))
    return cursor.fetchone() is not None

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
        command = row[2]
        generated_request = row[4]
        timestamp = row[5]
        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M")
        history_lines.append(f"Command {command} generated {generated_request} at {formatted_time}")
    return "\n".join(history_lines) if history_lines else "No history found."

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

# === Async handlers ===
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! Use /help to see the available commands.")

async def check_weather(update: Update, context: CallbackContext):
    username = update.effective_user.username
    if not is_user_authorized(username):
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    if len(context.args) < 2:
        response_text = "Please provide both city and date. Example: /check_weather London 2025-08-01"
    else:
        city, date = context.args[0], context.args[1]
        response_text = check_weather_logic(city, date)
        log_to_db(update.message.from_user.id, '/check_weather', context.args, response_text)

    await update.message.reply_text(response_text)

async def history(update: Update, context: CallbackContext):
    username = update.effective_user.username
    if not is_user_authorized(username):
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    if len(context.args) < 1:
        response_text = "Please provide limit number. Example: /history 5"
    else:
        try:
            limit = int(context.args[0])
            if limit > 10 or limit <= 0:
                response_text = "Please provide a valid number. The maximum allowed is 10."
            else:
                response_text = get_history_text(update.message.from_user.id, limit)
        except ValueError:
            response_text = "Invalid number format. Please provide a valid integer limit (max 10)."

    await update.message.reply_text(response_text)
    # log_to_db(update.message.from_user.id, '/history', context.args, response_text)

async def bot_info(update: Update, context: CallbackContext):
    await update.message.reply_text("This is a weather app by DM, version 1.0.")
    # log_to_db(update.message.from_user.id, '/bot_info', [], "Bot Info")

async def update_bot(update: Update, context: CallbackContext):
    await update.message.reply_text("Bot updated.")
    # log_to_db(update.message.from_user.id, '/update_bot', [], "Bot Updated")

async def unknown(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Here are the valid commands you can use:\n\n"
        "- /check_weather <city> <YYYY-MM-DD> - to get the weather for a specific city at a specific time\n"
        "- /bot_info - to get information about bot\n"
        "- /update_bot - to update bot version\n"
        "- /history <number> - to get history of requests"
    )

# === Main function ===
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check_weather", check_weather))
    application.add_handler(CommandHandler("history", history))
    application.add_handler(CommandHandler("bot_info", bot_info))
    application.add_handler(CommandHandler("update_bot", update_bot))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    application.run_polling()

if __name__ == '__main__':
    main()
