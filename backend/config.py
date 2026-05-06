from dotenv import load_dotenv
import os

load_dotenv()

# Parsea "CODIGO:Nombre,CODIGO2:Nombre2" → dict
def _parse_codes(raw: str) -> dict:
    result = {}
    for pair in raw.split(","):
        code, name = pair.split(":", 1)
        result[code.strip()] = name.strip()
    return result

USER_CODES = _parse_codes(os.getenv("USER_CODES", ""))
DEFAULT_ROOM = "general"
ROOMS = ["general", "gaming", "deberes", "examenes", "off-topic"]
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-key-insegura")
PORT = int(os.getenv("PORT", 8080))