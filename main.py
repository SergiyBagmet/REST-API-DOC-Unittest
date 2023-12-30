from fastapi import FastAPI

from src.routes import contacts, auth, users
from utils import health_checker
from utils.limiter import lifespan_limiter
from utils.cors import configure_cors, register_user_agent_ban_middleware

app = FastAPI(lifespan=lifespan_limiter)


configure_cors(app)
register_user_agent_ban_middleware(app)

app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(health_checker.router, prefix="/api")


@app.get("/")
def index():
    return {"message": "Address Book Application"}
