# ─────────────────────────────────────────────
#  auth.py  –  Lógica de autenticación por código
# ─────────────────────────────────────────────

from config import USER_CODES


def validate_code(code: str) -> dict | None:
    """
    Valida un código de acceso.
    Retorna {"code": ..., "username": ...} si es válido, None si no.
    """
    code = code.strip().upper()
    username = USER_CODES.get(code)
    if username:
        return {"code": code, "username": username}
    return None


def get_username(code: str) -> str | None:
    """Devuelve solo el apodo para un código, o None."""
    result = validate_code(code)
    return result["username"] if result else None