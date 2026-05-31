from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import time
import random

app = FastAPI(title="TIA Marketplace API")

# --- БАЗЫ ДАННЫХ (В оперативной памяти для старта) ---
users_db = {}  # { "TIA-12345": {"pass": "123", "role": "user", "pro_expiry": 0, "pro_status": "none"} }
ads_db = []    # Список всех объявлений
admin_pass = "admin123"

# --- МОДЕЛИ ДАННЫХ ---
class AuthRequest(BaseModel):
    password: str

class ProRequest(BaseModel):
    user_id: str

class AdModel(BaseModel):
    id: int
    user_id: str
    title: str
    desc: str
    price: float
    category: str
    status: str = "moderation"
    vip: bool = False

# --- ЭНДПОИНТЫ ---
@app.post("/api/register")
def register_user(req: AuthRequest):
    if len(req.password) < 3:
        raise HTTPException(status_code=400, detail="Пароль слишком короткий")
    
    # Генерация красивого ID
    new_id = f"TIA-{random.randint(10000, 99999)}"
    users_db[new_id] = {
        "pass": req.password, 
        "role": "user", 
        "pro_expiry": 0, 
        "pro_status": "none"
    }
    return {"status": "success", "user_id": new_id}

@app.post("/api/admin/login")
def admin_login(req: AuthRequest):
    if req.password != admin_pass:
        raise HTTPException(status_code=403, detail="Неверный пароль администратора")
    return {"status": "success", "role": "admin"}

@app.post("/api/ads/create")
def create_ad(ad: AdModel):
    ads_db.append(ad.dict())
    return {"status": "success", "message": "Отправлено на модерацию"}

@app.get("/api/admin/stats")
def get_admin_stats():
    active_pro = sum(1 for u in users_db.values() if u['pro_expiry'] > time.time())
    pending_ads = [a for a in ads_db if a['status'] == 'moderation']
    pending_pro = {k: v for k, v in users_db.items() if v['pro_status'] == 'pending'}
    
    return {
        "total_users": len(users_db),
        "total_revenue": active_pro * 95000,
        "pending_ads": pending_ads,
        "pending_pro_requests": pending_pro
    }

@app.post("/api/admin/approve_pro")
def approve_pro(req: ProRequest):
    if req.user_id in users_db:
        # Активация на 30 дней (в секундах)
        users_db[req.user_id]['pro_expiry'] = time.time() + (30 * 24 * 60 * 60)
        users_db[req.user_id]['pro_status'] = "approved"
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Пользователь не найден")

# Для запуска: pip install fastapi uvicorn
# Команда: uvicorn main:app --reload
