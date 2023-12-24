from fastapi import FastAPI

from src.routes import contacts, auth
from utils import health_checker
from utils.limiter import register_startup_event_limiter
from utils.cors import configure_cors

app = FastAPI()

register_startup_event_limiter(app)
configure_cors(app)

app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(health_checker.router, prefix="/api")


@app.get("/")
def index():
    return {"message": "Address Book Application"}
