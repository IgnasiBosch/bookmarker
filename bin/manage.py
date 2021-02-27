import os
import sys
import uvicorn
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

try:
    from src.asgi import app
except ImportError as exc:
    raise ImportError("Couldn't import FastApi Instance.")


def execute():
    uvicorn.run(
        "src.asgi:app",
        host="127.0.0.1",
        port=int(os.getenv("APP_PORT", 8000)),
        # fd=0,
        # uds="/tmp/bookmarker.sock",
        reload=True,
        workers=int(os.getenv("APP_WORKERS", 2)),
    )


action_map = {
    "serve": execute,
}

if __name__ == "__main__":
    args = sys.argv[1:]
    action = args[0]
    try:
        action_map[action]()
    except Exception as exc:
        print(exc)
        raise exc
