from config import ROOMS

# Salas fijas siempre presentes + las que se creen dinámicamente
_rooms: dict[str, dict[str, str]] = {room: {} for room in ROOMS}

_sessions: dict[str, tuple[str, str]] = {}


def join_room(sid: str, room: str, username: str):
    if room not in _rooms:
        _rooms[room] = {}
    _rooms[room][sid] = username
    _sessions[sid] = (room, username)


def leave_room(sid: str) -> tuple[str, str] | None:
    info = _sessions.pop(sid, None)
    if info:
        room, _ = info
        _rooms.get(room, {}).pop(sid, None)
        # Solo borra la sala si NO es una sala fija de config
        if not _rooms.get(room) and room not in ROOMS:
            _rooms.pop(room, None)
    return info


def get_users_in_room(room: str) -> list[str]:
    return list(_rooms.get(room, {}).values())


def get_available_rooms() -> list[str]:
    """Lista de salas disponibles (fijas + dinámicas con gente)."""
    return list(_rooms.keys())


def get_room_of(sid: str) -> str | None:
    info = _sessions.get(sid)
    return info[0] if info else None


def get_username_of(sid: str) -> str | None:
    info = _sessions.get(sid)
    return info[1] if info else None