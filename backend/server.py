# ─────────────────────────────────────────────
#  server.py  –  Servidor principal
#  Usa:  Flask + Flask-SocketIO
# ─────────────────────────────────────────────

import os
import uuid
import base64
from flask import Flask, request, jsonify, session, send_from_directory
from flask_socketio import SocketIO, emit, join_room as sio_join, leave_room as sio_leave
from flask_cors import CORS

from config import SECRET_KEY, DEFAULT_ROOM, PORT
from auth import validate_code
from database import init_db, save_message, get_recent_messages
import rooms as room_manager

# ── carpeta de uploads ──────────────────────
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

ALLOWED_IMAGE = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO = {"video/mp4", "video/webm", "video/quicktime"}
ALLOWED_TYPES = ALLOWED_IMAGE | ALLOWED_VIDEO

EXT_MAP = {
    "image/jpeg": ".jpg", "image/png": ".png",
    "image/gif":  ".gif", "image/webp": ".webp",
    "video/mp4":  ".mp4", "video/webm": ".webm",
    "video/quicktime": ".mov",
}

MAX_FILE_MB = 300

# ── App ──────────────────────────────────────
app = Flask(__name__, static_folder="../frontend", static_url_path="")
app.secret_key = SECRET_KEY
CORS(app)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    manage_session=False,
    max_http_buffer_size=200 * 1024 * 1024,
)

init_db()


# ═══════════════════════════════════════════
#  RUTAS HTTP
# ═══════════════════════════════════════════

@app.route("/")
def index():
    return app.send_static_file("login.html")

@app.route("/chat")
def chat():
    return app.send_static_file("chat.html")

@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOADS_DIR, filename)

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    user = validate_code(data.get("code", ""))
    if not user:
        return jsonify({"ok": False, "error": "Código inválido"}), 401
    session["code"] = user["code"]
    session["username"] = user["username"]
    return jsonify({"ok": True, "username": user["username"]})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/me")
def me():
    if "username" in session:
        return jsonify({"ok": True, "username": session["username"]})
    return jsonify({"ok": False}), 401


# ═══════════════════════════════════════════
#  EVENTOS WEBSOCKET
# ═══════════════════════════════════════════

@socketio.on("connect")
def on_connect():
    if "username" not in session:
        return False
    username = session["username"]
    room = DEFAULT_ROOM
    sid = request.sid
    try:
        room_manager.join_room(sid, room, username)
    except Exception as e:
        print(f"[!] Error al unir {username} a sala: {e}")
        return False
    sio_join(room)
    history = get_recent_messages(room, limit=50)
    emit("history", {"messages": history, "room": room})
    emit("user_joined", {"username": username}, to=room)
    emit("users_update", {"users": room_manager.get_users_in_room(room)}, to=room)
    emit("available_rooms", {"rooms": room_manager.get_available_rooms(), "current": room})
    print(f"[+] {username} conectado (sid={sid})")

@socketio.on("disconnect")
def on_disconnect():
    sid = request.sid
    info = room_manager.leave_room(sid)
    if info:
        room, username = info
        sio_leave(room)
        emit("user_left", {"username": username}, to=room)
        emit("users_update", {"users": room_manager.get_users_in_room(room)}, to=room)
        print(f"[-] {username} desconectado")

@socketio.on("send_message")
def on_message(data):
    if "username" not in session:
        return
    text = (data.get("text") or "").strip()
    if not text or len(text) > 1000:
        return
    sid = request.sid
    room = room_manager.get_room_of(sid) or DEFAULT_ROOM
    msg = save_message(room, session["username"], text, msg_type="text")
    emit("new_message", msg, to=room)

@socketio.on("send_file")
def on_file(data):
    if "username" not in session:
        return
    mime = (data.get("mime") or "").strip().lower()
    if mime not in ALLOWED_TYPES:
        emit("upload_error", {"msg": f"Tipo no permitido: {mime}"})
        return
    raw = data.get("data", "")
    if "," in raw:
        raw = raw.split(",", 1)[1]
    try:
        file_bytes = base64.b64decode(raw)
    except Exception:
        emit("upload_error", {"msg": "Archivo corrupto"})
        return

    if len(file_bytes) > MAX_FILE_MB * 1024 * 1024:
        emit("upload_error", {"msg": f"Archivo demasiado grande (máx {MAX_FILE_MB} MB)"})
        return

    filename = f"{uuid.uuid4().hex}{EXT_MAP.get(mime, '')}"
    with open(os.path.join(UPLOADS_DIR, filename), "wb") as f:
        f.write(file_bytes)
    media_type = "image" if mime in ALLOWED_IMAGE else "video"
    sid = request.sid
    room = room_manager.get_room_of(sid) or DEFAULT_ROOM
    msg = save_message(room, session["username"], f"/uploads/{filename}", msg_type=media_type)
    emit("new_message", msg, to=room)
    print(f"[file] {session['username']} subió {filename} ({len(file_bytes)/1024:.1f} KB)")

@socketio.on("typing")
def on_typing(data):
    if "username" not in session:
        return
    sid = request.sid
    room = room_manager.get_room_of(sid) or DEFAULT_ROOM
    emit("user_typing",
         {"username": session["username"], "typing": data.get("typing", False)},
         to=room, include_self=False)

@socketio.on("switch_room")
def on_switch_room(data):
    if "username" not in session:
        return
    new_room = data.get("room", "").strip()
    if not new_room or new_room not in room_manager.get_available_rooms():
        return
    sid = request.sid
    username = session["username"]
    old_room = room_manager.get_room_of(sid)
    if old_room == new_room:
        return

    sio_leave(old_room)
    room_manager.leave_room(sid)
    emit("user_left", {"username": username}, to=old_room)
    emit("users_update", {"users": room_manager.get_users_in_room(old_room)}, to=old_room)

    room_manager.join_room(sid, new_room, username)
    sio_join(new_room)
    history = get_recent_messages(new_room, limit=50)
    emit("history", {"messages": history, "room": new_room})
    emit("user_joined", {"username": username}, to=new_room)
    emit("users_update", {"users": room_manager.get_users_in_room(new_room)}, to=new_room)
    emit("available_rooms", {"rooms": room_manager.get_available_rooms(), "current": new_room})


# ═══════════════════════════════════════════
#  ARRANQUE
# ═══════════════════════════════════════════

if __name__ == "__main__":
    print(f"Servidor en http://localhost:{PORT}")
    socketio.run(app, host="0.0.0.0", port=PORT, debug=True)