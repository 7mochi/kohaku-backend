CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    discord_id TEXT NOT NULL,
    discord_username TEXT NOT NULL,
    osu_id TEXT NULL,
    osu_username TEXT NULL,
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    verification_code TEXT NULL,
    access_token TEXT NULL,
    refresh_token TEXT NULL,
    token_expires_on TIMESTAMPTZ NULL,
    session_id UUID NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
