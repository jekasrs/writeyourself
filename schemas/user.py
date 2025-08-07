from pydantic import BaseModel, EmailStr, validator
import re

class UserCreate(BaseModel):
    phone: str
    email: EmailStr
    full_name: str
    password: str

    @validator("phone")
    def validate_russian_phone(cls, v):
        if not re.fullmatch(r"\+7\d{10}", v):
            raise ValueError("Введите номер в формате +7XXXXXXXXXX")
        return v

    @validator("password")
    def validate_password_length(cls, v):
        if len(v) < 7:
            raise ValueError("Пароль должен быть минимум 7 символов")
        return v