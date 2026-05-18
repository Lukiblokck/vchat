import threading
from config import ROOMS

_rooms: dict[str, dict[str, str]] = {room: {} for room in ROOMS}
_sessions: dict[str, tuple[str, str]] = {}
_lock = threading.Lock()


def join_room(sid: str, room: str, username: str):
    with _lock:
        if room not in _rooms:
            _rooms[room] = {}
        _rooms[room][sid] = username
        _sessions[sid] = (room, username)


def leave_room(sid: str) -> tuple[str, str] | None:
    with _lock:
        info = _sessions.pop(sid, None)
        if info:
            room, _ = info
            _rooms.get(room, {}).pop(sid, None)
            if not _rooms.get(room) and room not in ROOMS:
                _rooms.pop(room, None)
        return info


def get_users_in_room(room: str) -> list[str]:
    with _lock:
        # Deduplica por si el mismo user tiene varias pestañas
        return list(dict.fromkeys(_rooms.get(room, {}).values()))


def get_available_rooms() -> list[str]:
    with _lock:
        return list(_rooms.keys())


def get_room_of(sid: str) -> str | None:
    with _lock:
        info = _sessions.get(sid)
        return info[0] if info else None


def get_username_of(sid: str) -> str | None:
    with _lock:
        info = _sessions.get(sid)
        return info[1] if info else None