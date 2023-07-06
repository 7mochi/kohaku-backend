CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    discord_id TEXT NOT NULL,
    username TEXT NOT NULL,
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    verification_code TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
