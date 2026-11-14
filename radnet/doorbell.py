"""Experimental loopback-only, read-only RadNet socket preview.

No shell, posting, credentials, or public interface. Not a remote BBS release.
"""
import socket
from .terminal import page, safe_text

HOST = "127.0.0.1"
MAX_LINE = 64
MAX_DRAIN = 4096
TIMEOUT = 15.0
MENU = ("RADNET:// PRIVATE PREVIEW // READ ONLY\n"
        "LOCAL LOOPBACK ONLY / NO AUTHENTICATION\n"
        "[1] BOARDS [2] STATUS [3] LOG INFO [4] RESOURCES\n"
        "[5] DIRECTORY [6] EMERGENCY INFO [7] CAPABILITIES\n"
        "[0] DISCONNECT\n> ")


def handle_client(conn, db_path):
    """One bounded request per connection. Never dispatch to shell or writers."""
    conn.settimeout(TIMEOUT)
    conn.sendall(MENU.encode("utf-8"))
    try:
        data = bytearray()
        while len(data) <= MAX_LINE:
            chunk = conn.recv(1)
            if not chunk or chunk in (b"\n", b"\r"):
                break
            data.extend(chunk)
        if len(data) > MAX_LINE:
            # Drain a bounded remainder to avoid an unread-data TCP reset
            # swallowing the rejection on Linux.
            drained = 0
            while drained < MAX_DRAIN:
                chunk = conn.recv(min(256, MAX_DRAIN - drained))
                if not chunk or b"\n" in chunk or b"\r" in chunk:
                    break
                drained += len(chunk)
            reply = "Input too long. Disconnected."
        else:
            try:
                choice = data.decode("utf-8").strip()
            except UnicodeDecodeError:
                choice = ""
            if choice == "0":
                reply = "Disconnected."
            elif choice in "1234567" and len(choice) == 1:
                reply = page(choice, db_path)
            else:
                reply = "Unknown selection. No commands executed."
        # Preserve intentional line boundaries while sanitizing each line.
        # safe_text() strips control characters, including newline itself.
        clean = "\
".join(safe_text(line, 8192) for line in reply.splitlines())
        conn.sendall((clean[:8192] + "\
").encode("utf-8"))
    except (socket.timeout, BrokenPipeError, ConnectionResetError):
        return


def serve(db_path, port=0, ready=None, stop=None):
    """Bind exclusively to IPv4 loopback. One client at a time."""
    if not 0 <= port <= 65535:
        raise ValueError("Invalid port")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind((HOST, port))
        listener.listen(1)
        listener.settimeout(0.25)
        if ready is not None:
            ready(listener.getsockname()[1])
        while stop is None or not stop.is_set():
            try:
                conn, _ = listener.accept()
            except socket.timeout:
                continue
            with conn:
                handle_client(conn, db_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Loopback-only RadNet read-only preview")
    parser.add_argument("--db", default="radnet-dev.sqlite3")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    print(f"RadNet read-only preview on {HOST}:{args.port} (NO AUTH; LOOPBACK ONLY)", flush=True)
    serve(args.db, port=args.port)
