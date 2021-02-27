from fastapi import FastAPI

from src.config import Config

app = FastAPI()
config = Config()


@app.get("/health")
def health():
    return {"status": "ok"}
