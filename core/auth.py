from fastapi import Request, HTTPException, Depends
from itsdangerous import URLSafeSerializer
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.config import SECRET_KEY
from app.db.database import SessionLocal
from app.models.user import User

serializer = URLSafeSerializer(SECRET_KEY, salt="session")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_session_token(user_id: int):
    return serializer.dumps({"user_id": user_id})

def get_user_id_from_token(token: str):
    try:
        data = serializer.loads(token)
        return data["user_id"]
    except Exception:
        return None

def get_current_user(request: Request, db=Depends(get_db)):
    session_token = request.cookies.get("session_token")
    user_id = get_user_id_from_token(session_token)
    if not user_id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    return user