import re
import typing as t

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


def configure_cors(app: FastAPI):
    """
    The configure_cors function configures the CORS settings for our FastAPI application.

    :param app: FastAPI: Pass the fastapi instance to the function
    :return: None
    :doc-author: Trelent
    """
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
    """
    The register_user_agent_ban_middleware function registers a middleware that checks the user-agent header of each request.
    If it matches any of the banned patterns, then it returns a 403 Forbidden response. Otherwise, it calls the next function in
    the chain.

    :param app: FastAPI: Pass the fastapi instance to the function
    :return: A middleware function
    :doc-author: Trelent
    """
    @app.middleware("http")
    async def user_agent_ban_middleware(request: Request, call_next: t.Callable):
        """
        The user_agent_ban_middleware function is a middleware function that checks the user-agent header of an incoming request.
        If the user-agent matches any of the banned_user_agent_patterns, then it returns a 403 Forbidden response with a detail message.
        Otherwise, it calls call_next and returns its response.

        :param request: Request: Get the user-agent from the request header
        :param call_next: t.Callable: Pass the request to the next middleware function
        :return: A json response with a status code of 403 and the message &quot;you are banned&quot; if the user agent matches one of the ban patterns
        :doc-author: Trelent
        """
        user_agent = request.headers.get("user-agent")
        banned_user_agent_patterns = [re.compile(ban_pattern) for ban_pattern in user_agent_ban_list]
        if any(pattern.match(user_agent) for pattern in banned_user_agent_patterns):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "You are banned"},
            )
        response = await call_next(request)
        return response
