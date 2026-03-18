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
    "V2I0C1T0OR": "Victor",
    "D2A0N1I0": "Dani",
    "J2U0A1N1": "Juan Pablo",
    "U2R0K1O1": "Urko",
    "J2U0L1E1N": "Julen",
    "E2G0O1R1": "Egor",
    "I2K0E1R1": "Iker O",
}

# Sala general por defecto
DEFAULT_ROOM = "general"

# Más salas que se pueden usar, si quieren
ROOMS = ["general", "gaming", "deberes", "secreto"]

# Clave secreta para las sesiones Flask (cámbiala por algo aleatorio)
SECRET_KEY = "skibidi-sigma-pomni-digital-fortnite-chamba"

# Puerto del servidor
PORT = 8080