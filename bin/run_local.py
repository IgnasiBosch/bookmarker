#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

if __name__ == "__main__":
    import uvicorn

    load_dotenv()
    BASEDIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(BASEDIR)

    uvicorn.run(
        "src.asgi:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        workers=int(os.getenv("APP_WORKERS", 1)),
        reload=True,
    )
