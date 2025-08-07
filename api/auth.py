from fastapi import APIRouter, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.auth import get_db, create_session_token, get_current_user
from app.schemas.user import UserCreate
from app.core.security import hash_password
from app.core.security import verify_password
from fastapi import Request, Depends
from app.models.user import User

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/register", response_class=HTMLResponse)
def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
def post_register(
    request: Request,
    phone: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        schema = UserCreate(phone=phone, email=email, full_name=full_name, password=password)
    except ValidationError as e:
        errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        return templates.TemplateResponse("register.html", {
            "request": request,
            "errors": errors,
            "values": {"phone": phone, "email": email, "full_name": full_name}
        })

    if db.query(User).filter((User.email == email) | (User.phone == phone)).first():
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Email или номер уже заняты",
            "values": {"phone": phone, "email": email, "full_name": full_name}
        })

    user = User(
        phone=schema.phone,
        email=schema.email,
        full_name=schema.full_name,
        hashed_password=hash_password(schema.password)
    )
    db.add(user)
    db.commit()

    response = RedirectResponse(url="/login", status_code=302)
    return response


@router.get("/login", response_class=HTMLResponse)
def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def post_login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный email или пароль"})

    # Сессия
    session_token = create_session_token(user.id)
    response = RedirectResponse(url="/writeyourself", status_code=302)
    response.set_cookie("session_token", session_token, httponly=True)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session_token")
    return response


@router.get("/writeyourself", response_class=HTMLResponse)
def writeyourself(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})