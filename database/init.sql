CREATE TABLE telegram_logs (
    id SERIAL PRIMARY KEY, 
    user_id INTEGER NOT NULL, 
    command TEXT NOT NULL, 
    args TEXT, 
    response_text TEXT NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE telegram_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL
);