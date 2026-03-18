# ─────────────────────────────────────────────
#  rooms.py  –  Gestión de salas y conexiones
# ─────────────────────────────────────────────

# Estructura en memoria: { room_name: { sid: username } }
_rooms: dict[str, dict[str, str]] = {}

# Mapa inverso: sid → (room, username)  para desconexiones rápidas
_sessions: dict[str, tuple[str, str]] = {}


def join_room(sid: str, room: str, username: str):
    """Registra que un socket (sid) entró a una sala."""
    if room not in _rooms:
        _rooms[room] = {}
    _rooms[room][sid] = username
    _sessions[sid] = (room, username)


def leave_room(sid: str) -> tuple[str, str] | None:
    """
    Elimina al usuario cuando se desconecta.
    Devuelve (room, username) o None si no existía.
    """
    info = _sessions.pop(sid, None)
    if info:
        room, _ = info
        _rooms.get(room, {}).pop(sid, None)
        if not _rooms.get(room):          # sala vacía → la borra
            _rooms.pop(room, None)
    return info


def get_users_in_room(room: str) -> list[str]:
    """Lista de apodos en una sala."""
    return list(_rooms.get(room, {}).values())


def get_room_of(sid: str) -> str | None:
    info = _sessions.get(sid)
    return info[0] if info else None


def get_username_of(sid: str) -> str | None:
    info = _sessions.get(sid)
    return info[1] if info else None