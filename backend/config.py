from dotenv import load_dotenv
import os
import warnings

load_dotenv()

def _parse_codes(raw: str) -> dict:
    result = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if ":" not in pair:
            warnings.warn(f"USER_CODES: par mal formado ignorado: {repr(pair)}")
            continue
        code, name = pair.split(":", 1)
        result[code.strip()] = name.strip()
    return result

USER_CODES = _parse_codes(os.getenv("USER_CODES", ""))
DEFAULT_ROOM = "general"
ROOMS = ["general", "gaming", "deberes", "examenes", "off-topic"]

_secret = os.getenv("SECRET_KEY", "")
if not _secret:
    warnings.warn("SECRET_KEY no definida en .env — usando clave insegura", stacklevel=2)
    _secret = "fallback-key-insegura"
SECRET_KEY = _secret

PORT = int(os.getenv("PORT", 8080))