import time
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI(title="TIA Secure Enterprise Marketplace API Backend Engine", version="6.0.0")

# --- СЕРВЕРНЫЕ РЕЕСТРЫ ХРАНЕНИЯ ДАННЫХ ---
USERS_REGISTRY: Dict[str, dict] = {}
ADS_DATABASE: List[dict] = []
ADMIN_SECRET_KEY: str = "admin"

class RegistrationPayload(BaseModel):
    name: str
    phone: str
    password: str

class LoginPayload(BaseModel):
    user_id: str
    password: str

class VerificationRequest(BaseModel):
    user_id: str

class AdPublishPayload(BaseModel):
    category: str
    title: str
    price: float
    district: str
    desc: str
    phone: str
    images: List[str]
    custom_fields: List[Dict[str, str]]
    user_id: str
    vip: bool

@app.post("/api/auth/register", summary="Обязательная защищенная регистрация продавца")
def register_vendor(payload: RegistrationPayload):
    if len(payload.password) < 4:
        raise HTTPException(status_code=400, detail="Пароль безопасности слишком короткий.")
    
    generated_id = f"TIA-{random.randint(10000, 99999)}"
    while generated_id in USERS_REGISTRY:
        generated_id = f"TIA-{random.randint(10000, 99999)}"
        
    USERS_REGISTRY[generated_id] = {
        "name": payload.name,
        "phone": payload.phone,
        "password": payload.password,
        "pro_expiry": 0,
        "pro_request": "none"
    }
    return {"status": "success", "user_id": generated_id, "name": payload.name}

@app.post("/api/auth/login", summary="Аутентификация по ID")
def login_vendor(payload: LoginPayload):
    user = USERS_REGISTRY.get(payload.user_id)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Ошибка безопасности.")
    return {"status": "success", "user_id": payload.user_id, "name": user["name"]}

@app.post("/api/admin/approve_pro")
def approve_pro_tier(payload: VerificationRequest, token: str):
    if token != ADMIN_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Отказ авторизации.")
    if payload.user_id not in USERS_REGISTRY:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")
    
    duration_30_days_ms = 30 * 24 * 60 * 60 * 1000
    USERS_REGISTRY[payload.user_id]["pro_expiry"] = int(time.time() * 1000) + duration_30_days_ms
    USERS_REGISTRY[payload.user_id]["pro_request"] = "approved"
    return {"status": "success", "message": "PRO статус подтвержден."}
