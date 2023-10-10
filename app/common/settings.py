from __future__ import annotations

import os

from dotenv import load_dotenv


def read_bool(value: str) -> bool:
    return value.lower() == "true"


load_dotenv()

# asgi + app
APP_ENV = os.environ["APP_ENV"]
APP_HOST = os.environ["APP_HOST"]
APP_PORT = os.environ["APP_PORT"]
APP_LOG_LEVEL = os.environ["APP_LOG_LEVEL"]

# frontend
FRONTEND_HOST = os.environ["FRONTEND_HOST"]
FRONTEND_PORT = os.environ["FRONTEND_PORT"]
# TODO: improve this
FRONTEND_URL = (
    f"http://{FRONTEND_HOST}{'' if FRONTEND_PORT == '80' else f':{FRONTEND_PORT}'}"
)

# domain
DOMAIN = os.environ["DOMAIN"]

# database
READ_DB_SCHEME = os.environ["READ_DB_SCHEME"]
READ_DB_HOST = os.environ["READ_DB_HOST"]
READ_DB_PORT = int(os.environ["READ_DB_PORT"])
READ_DB_USER = os.environ["READ_DB_USER"]
READ_DB_PASS = os.environ["READ_DB_PASS"]
READ_DB_NAME = os.environ["READ_DB_NAME"]
READ_DB_CA_CERT_BASE64 = os.environ["READ_DB_CA_CERT_BASE64"]
READ_DB_MIN_POOL_SIZE = int(os.environ["READ_DB_MIN_POOL_SIZE"])
READ_DB_MAX_POOL_SIZE = int(os.environ["READ_DB_MAX_POOL_SIZE"])
READ_DB_USE_SSL = read_bool(os.environ["READ_DB_USE_SSL"])

WRITE_DB_SCHEME = os.environ["WRITE_DB_SCHEME"]
WRITE_DB_HOST = os.environ["WRITE_DB_HOST"]
WRITE_DB_PORT = int(os.environ["WRITE_DB_PORT"])
WRITE_DB_USER = os.environ["WRITE_DB_USER"]
WRITE_DB_PASS = os.environ["WRITE_DB_PASS"]
WRITE_DB_NAME = os.environ["WRITE_DB_NAME"]
WRITE_DB_CA_CERT_BASE64 = os.environ["WRITE_DB_CA_CERT_BASE64"]
WRITE_DB_MIN_POOL_SIZE = int(os.environ["WRITE_DB_MIN_POOL_SIZE"])
WRITE_DB_MAX_POOL_SIZE = int(os.environ["WRITE_DB_MAX_POOL_SIZE"])
WRITE_DB_USE_SSL = read_bool(os.environ["WRITE_DB_USE_SSL"])

# discord
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
DISCORD_GUILD_ID = int(os.environ["DISCORD_GUILD_ID"])
DISCORD_VERIFY_CHANNEL_ID = int(os.environ["DISCORD_VERIFY_CHANNEL_ID"])
DISCORD_VERIFIED_ROLE_ID = int(os.environ["DISCORD_VERIFIED_ROLE_ID"])

# osu
OSU_CLIENT_ID = int(os.environ["OSU_CLIENT_ID"])
OSU_CLIENT_SECRET = os.environ["OSU_CLIENT_SECRET"]
OSU_REDIRECT_URI = os.environ["OSU_REDIRECT_URI"]

# session
SESSION_COOKIE_NAME = os.environ["SESSION_COOKIE_NAME"]
SESSION_COOKIE_IDENTIFIER = os.environ["SESSION_COOKIE_IDENTIFIER"]
SESSION_COOKIE_KEY = os.environ["SESSION_COOKIE_KEY"]
