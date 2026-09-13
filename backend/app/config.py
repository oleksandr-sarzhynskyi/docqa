from os import getenv

API_KEY = getenv("GEMINI_API_KEY")
MODEL = getenv("MODEL")
DATABASE_URL = getenv("DATABASE_URL")
REDIS_URL = getenv("REDIS_URL")
SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)

required = {
    "GEMINI_API_KEY": API_KEY,
    "MODEL": MODEL,
    "DATABASE_URL": DATABASE_URL,
    "REDIS_URL": REDIS_URL,
    "SECRET_KEY": SECRET_KEY,
    "ACCESS_TOKEN_EXPIRE_MINUTES": ACCESS_TOKEN_EXPIRE_MINUTES
}

for name, value in required.items():
    if value is None:
        raise ValueError(f"{name} was not found.")