CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY, 
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT FALSE,
    email_verify_token TEXT
);

CREATE TABLE IF NOT EXISTS forgot_password (
    fp_id INTEGER PRIMARY KEY, 
    email TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    hashed_timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_login_check (
    login_id INTEGER PRIMARY KEY, 
    username TEXT UNIQUE NOT NULL,
    first_time TIMESTAMP NOT NULL,
    login_attempts INTEGER NOT NULL
);