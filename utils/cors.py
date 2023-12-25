import re
import typing as t

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


def configure_cors(app: FastAPI):
    origins = ["http://localhost:3000", "http://localhost:8000"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    )


user_agent_ban_list = [r"Googlebot", r"Python-urllib"]  # TODO add more and make in file with interface add/remove


def register_user_agent_ban_middleware(app: FastAPI):
    @app.middleware("http")
    async def user_agent_ban_middleware(request: Request, call_next: t.Callable):
        # print(request.headers.get("Authorization"))
        user_agent = request.headers.get("user-agent")
        banned_user_agent_patterns = [re.compile(ban_pattern) for ban_pattern in user_agent_ban_list]
        if any(pattern.match(user_agent) for pattern in banned_user_agent_patterns):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "You are banned"},
            )
        response = await call_next(request)
        return response
