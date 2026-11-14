"""Read-only, bounded board presentation for the experimental loopback Doorbell."""
from .boards import Boards, BoardError
from .terminal import safe_text


def board_list(db_path):
    try:
        boards = Boards(db_path).boards()
    except BoardError:
        return "MESSAGE BOARDS\nJournal unavailable.", []
    lines = ["MESSAGE BOARDS // LOCAL", "AUTHORS UNVERIFIED", "READ ONLY", ""]
    for i, board in enumerate(boards, 1):
        lines.append(f"[{i}] {safe_text(board['title'], 100)}")
    if not boards:
        lines.append("No local boards yet.")
    return "\n".join(lines), boards


def post_list(db_path, board, number=1):
    try:
        posts = Boards(db_path).messages(board["id"], number)
    except BoardError:
        return "POSTS\nJournal unavailable.", []
    lines = [f"BOARD: {safe_text(board['title'], 100)}", f"POSTS // PAGE {number}", "AUTHORS UNVERIFIED", ""]
    for i, post in enumerate(posts, 1):
        lines.append(f"[{i}] {safe_text(post['title'], 100)}")
        lines.append(f"  By {safe_text(post['author'], 32)}")
    if not posts:
        lines.append("No posts on this page.")
    return "\n".join(lines), posts


def post_detail(post):
    return "\n".join([
        "POST // LOCAL ARCHIVE",
        safe_text(post["title"], 100),
        "By " + safe_text(post["author"], 32) + " [UNVERIFIED]",
        "Event: " + safe_text(post["id"], 64),
        "Reply to: " + (safe_text(post["parent"], 64) if post["parent"] else "none"),
        "",
        safe_text(post["body"], 4000),
    ])
