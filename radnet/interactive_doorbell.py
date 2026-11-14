"""Experimental multi-selection loopback session, read-only and unauthenticated.

Distinct from the known-good one-request doorbell. Never expose publicly.
"""
import argparse
import socket

from .doorbell import HOST, MAX_LINE

# Interactive reading sessions have their own timeout; the one-shot
# Doorbell remains deliberately short-lived.
INTERACTIVE_TIMEOUT = 300.0
from .terminal import page
from .presentation import render_remote, normalized_width
from .capability_screen import dashboard, evidence_listing
from .remote_boards import board_list, post_list, post_detail
from .remote_log import entries, detail, revisions

MAX_SELECTIONS = 20
MAX_DRAIN = 4096

WELCOME = ("RADNET:// PRIVATE PREVIEW\n"
           "READ ONLY // NO AUTHENTICATION\n"
           "LOOPBACK ONLY\n"
           "[1] BOARDS  [2] STATUS\n"
           "[3] LOG INFO  [4] RESOURCES\n"
           "[5] DIRECTORY  [6] EMERGENCY\n"
           "[7] CAPABILITIES  [0] DISCONNECT")


def send_text(conn, message, width=None):
    conn.sendall(render_remote(message, width).encode("utf-8"))


def read_selection(conn):
    """Return (selection, reason). One line, bounded, EOF-aware."""
    data = bytearray()
    while True:
        char = conn.recv(1)
        if not char:
            return None, "eof"
        if char in (b"\r", b"\n"):
            break
        data.extend(char)
        if len(data) > MAX_LINE:
            drained = 0
            while drained < MAX_DRAIN:
                chunk = conn.recv(min(256, MAX_DRAIN - drained))
                if not chunk or b"\n" in chunk or b"\r" in chunk:
                    break
                drained += len(chunk)
            return None, "oversized"
    try:
        return data.decode("utf-8").strip(), None
    except UnicodeDecodeError:
        return None, "invalid"


def registry_body(db_path, width):
    """Avoid duplicating menu instructions already owned by the session."""
    return dashboard(db_path, width).removesuffix(
        "[1] VIEW CAPABILITY EVIDENCE\n[0] RETURN"
    )


def handle_session(conn, db_path, width=None, idle_timeout=INTERACTIVE_TIMEOUT):
    """Finite read-only session with explicit per-client navigation state."""
    conn.settimeout(idle_timeout)
    width = normalized_width(width)
    screen = "main"
    boards = []
    posts = []
    selected_board = None
    page_number = 1
    log_page = 1
    log_records = []
    selected_log = None
    revision_records = []
    revision_page = 1
    try:
        send_text(conn, WELCOME + "\n> ", width)
        for _ in range(MAX_SELECTIONS):
            choice, error = read_selection(conn)
            if error == "eof":
                return
            if error == "oversized":
                send_text(conn, "Input too long. Disconnected.", width)
                return
            if error == "invalid":
                send_text(conn, "Invalid encoding. Disconnected.", width)
                return

            if screen == "main":
                if choice == "0":
                    send_text(conn, "Disconnected.", width)
                    return
                if choice == "1":
                    screen = "boards"
                    body, boards = board_list(db_path)
                    send_text(conn, body, width)
                elif choice == "3":
                    screen = "log"
                    log_page = 1
                    body, log_records = entries(db_path, log_page)
                    send_text(conn, body, width)
                elif choice == "7":
                    screen = "registry"
                    send_text(conn, registry_body(db_path, width), width)
                elif len(choice) == 1 and choice in "2456":
                    send_text(conn, page(choice, db_path), width)
                else:
                    send_text(conn, "Unknown selection.\nNo commands executed.", width)
            elif screen == "boards":
                if choice == "0":
                    screen = "main"
                    send_text(conn, "Returned to main menu.\n" + WELCOME, width)
                elif choice.isascii() and choice.isdecimal() and 1 <= int(choice) <= len(boards):
                    selected_board = boards[int(choice) - 1]
                    page_number = 1
                    screen = "posts"
                    body, posts = post_list(db_path, selected_board, page_number)
                    send_text(conn, body, width)
                else:
                    send_text(conn, "Unknown selection.\nNo commands executed.", width)
            elif screen == "posts":
                if choice == "0":
                    screen = "boards"
                    body, boards = board_list(db_path)
                    send_text(conn, body, width)
                elif choice == ">" and len(posts) == 10 and page_number < 10000:
                    page_number += 1
                    body, posts = post_list(db_path, selected_board, page_number)
                    send_text(conn, body, width)
                elif choice == "<" and page_number > 1:
                    page_number -= 1
                    body, posts = post_list(db_path, selected_board, page_number)
                    send_text(conn, body, width)
                elif choice.isascii() and choice.isdecimal() and 1 <= int(choice) <= len(posts):
                    screen = "post"
                    send_text(conn, post_detail(posts[int(choice) - 1]), width)
                else:
                    send_text(conn, "Unknown selection.\nNo commands executed.", width)
            elif screen == "post":
                if choice == "0":
                    screen = "posts"
                    body, posts = post_list(db_path, selected_board, page_number)
                    send_text(conn, body, width)
                else:
                    send_text(conn, "Unknown selection.\nNo commands executed.", width)
            elif screen == "log":
                if choice == "0":
                    screen = "main"
                    send_text(conn, "Returned to main menu.\n" + WELCOME.split("\n> ")[0], width)
                elif choice == ">" and len(log_records) == 10 and log_page < 10000:
                    log_page += 1
                    body, log_records = entries(db_path, log_page)
                    send_text(conn, body, width)
                elif choice == "<" and log_page > 1:
                    log_page -= 1
                    body, log_records = entries(db_path, log_page)
                    send_text(conn, body, width)
                elif choice.isascii() and choice.isdecimal() and 1 <= int(choice) <= len(log_records):
                    selected_log = log_records[int(choice) - 1]
                    screen = "log_detail"
                    send_text(conn, detail(selected_log), width)
                else:
                    send_text(conn, "Unknown selection.\nNo commands executed.", width)
            elif screen == "log_detail":
                if choice == "0":
                    screen = "log"
                    body, log_records = entries(db_path, log_page)
                    send_text(conn, body, width)
                elif choice.lower() == "h":
                    screen = "log_history"
                    revision_page = 1
                    body, revision_records = revisions(db_path, selected_log["entry_id"], revision_page)
                    send_text(conn, body, width)
                else:
                    send_text(conn, "Unknown selection.\nNo commands executed.", width)
            elif screen == "log_history":
                if choice == "0":
                    screen = "log_detail"
                    send_text(conn, detail(selected_log), width)
                elif choice == ">" and len(revision_records) == 10 and revision_page < 10000:
                    revision_page += 1
                    body, revision_records = revisions(db_path, selected_log["entry_id"], revision_page)
                    send_text(conn, body, width)
                elif choice == "<" and revision_page > 1:
                    revision_page -= 1
                    body, revision_records = revisions(db_path, selected_log["entry_id"], revision_page)
                    send_text(conn, body, width)
                elif choice.isascii() and choice.isdecimal() and 1 <= int(choice) <= len(revision_records):
                    screen = "log_revision"
                    send_text(conn, detail(revision_records[int(choice) - 1]), width)
                else:
                    send_text(conn, "Unknown selection.\nNo commands executed.", width)
            elif screen == "log_revision":
                if choice == "0":
                    screen = "log_history"
                    body, revision_records = revisions(db_path, selected_log["entry_id"], revision_page)
                    send_text(conn, body, width)
                else:
                    send_text(conn, "Unknown selection.\nNo commands executed.", width)
            elif screen == "registry":
                if choice == "0":
                    screen = "main"
                    send_text(conn, "Returned to main menu.\n" + WELCOME.split("\n> ")[0], width)
                elif choice == "1":
                    screen = "evidence"
                    send_text(conn, evidence_listing(db_path, width), width)
                else:
                    send_text(conn, "Unknown selection.\nNo commands executed.", width)
            elif screen == "evidence":
                if choice == "0":
                    screen = "registry"
                    send_text(conn, registry_body(db_path, width), width)
                else:
                    send_text(conn, "Unknown selection.\nNo commands executed.", width)

            if screen == "main":
                prompt = "> "
            elif screen == "boards":
                prompt = "[1-9] BOARD  [0] MAIN\n> "
            elif screen == "posts":
                prompt = "[1-9] POST  [< >] PAGE  [0] BACK\n> "
            elif screen == "post":
                prompt = "[0] BACK TO POSTS\n> "
            elif screen == "log":
                prompt = "[1-9] ENTRY [< >] PAGE [0] BACK\n> "
            elif screen == "log_detail":
                prompt = "[H] HISTORY [0] BACK\n> "
            elif screen == "log_history":
                prompt = "[1-9] REV [< >] PAGE [0] BACK\n> "
            elif screen == "log_revision":
                prompt = "[0] BACK TO HISTORY\n> "
            elif screen == "registry":
                prompt = "[1] EVIDENCE  [0] RETURN\n> "
            else:
                prompt = "[0] RETURN TO REGISTRY\n> "
            send_text(conn, prompt.rstrip(), width)
        send_text(conn, "Session limit reached. Disconnected.", width)
    except (socket.timeout, BrokenPipeError, ConnectionResetError):
        return


def serve(db_path, port=0, ready=None, stop=None, width=None, idle_timeout=INTERACTIVE_TIMEOUT):
    """Only IPv4 loopback; serial connections; no background worker threads."""
    if not 0 <= port <= 65535:
        raise ValueError("Invalid port")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((HOST, port))
        listener.listen(1)
        listener.settimeout(0.25)
        if ready:
            ready(listener.getsockname()[1])
        while stop is None or not stop.is_set():
            try:
                conn, _ = listener.accept()
            except socket.timeout:
                continue
            with conn:
                handle_session(conn, db_path, width, idle_timeout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Experimental interactive RadNet loopback preview")
    parser.add_argument("--db", default="radnet-dev.sqlite3")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--width", type=int, default=36, help="client display columns (24-160)")
    parser.add_argument("--idle-timeout", type=float, default=INTERACTIVE_TIMEOUT, help="socket idle timeout in seconds (default: 300)")
    args = parser.parse_args()
    print(f"RadNet interactive preview on {HOST}:{args.port} (READ ONLY; NO AUTH)", flush=True)
    if not 1 <= args.idle_timeout <= 86400:
        parser.error("--idle-timeout must be between 1 and 86400 seconds")
    serve(args.db, args.port, width=args.width, idle_timeout=args.idle_timeout)
