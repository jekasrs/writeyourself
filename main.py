from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.core.auth import get_user_id_from_token
from app.db.database import Base, engine
from app.api import auth

PUBLIC_PATHS = ["/login", "/register", "/static", "/favicon.ico"]

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if any(path.startswith(p) for p in PUBLIC_PATHS):
            return await call_next(request)

        token = request.cookies.get("session_token")
        user_id = get_user_id_from_token(token)

        if not user_id:
            return RedirectResponse("/login")

        return await call_next(request)

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.add_middleware(AuthMiddleware)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.include_router(auth.router)


