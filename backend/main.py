from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.firebase import db
from routers import user_router, search_router

app = FastAPI(
    title="Smart Tourism API",
    description="API hệ thống du lịch thông minh.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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