# ─────────────────────────────────────────────
#  config.py  –  Ajusta esto con tus amigos
# ─────────────────────────────────────────────

# Diccionario: CÓDIGO → apodo visible en el chat
# Comparte cada código solo con quien quieras que entre.
USER_CODES = {
    "A2I0T1O0RF": "Aitor F",
    "I2Z0A1N1": "Izan",
    "2A0I1T1ORN": "Aitor N",
    "N2I0K1O1LAI": "Nikolai",
    "J2U0A1N1": "Juan Pablo",
}

# Sala general por defecto
DEFAULT_ROOM = "general"

# Más salas que se pueden usar, si quieren
ROOMS = ["general", "gaming", "deberes", "examenes", "off-topic"]

# Clave secreta para las sesiones Flask (cámbiala por algo aleatorio)
SECRET_KEY = "skibidi-sigma-pomni-digital-fortnite-chamba"

# Puerto del servidor
PORT = 8080