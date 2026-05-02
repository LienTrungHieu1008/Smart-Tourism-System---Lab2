from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.firebase import db
from routers import user_router, search_router

app = FastAPI(
    title="Smart Tourism API",
    description="API hệ thống du lịch thông minh. Đã được chia tách chuẩn mô hình Backend / Frontend.",
    version="2.0.0"
)

# Thêm CORS Middleware để cho phép Frontend (chạy ở cổng hoặc tên miền khác) gọi API tới Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cho phép mọi nguồn
    allow_credentials=True,
    allow_methods=["*"], # Cho phép mọi phương thức (GET, POST, OPTIONS...)
    allow_headers=["*"], # Cho phép mọi Headers (kể cả Authorization Bearer Token)
)

# Gắn các API router vào
app.include_router(user_router.router)
app.include_router(search_router.router)

@app.get("/")
def read_root():
    return {
        "system": "Smart Tourism API",
        "firebase_connected": db is not None,
        "message": "Hệ thống Backend đã chạy thành công!"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "firebase": "connected" if db else "disconnected"
    }