from fastapi import APIRouter, Depends, HTTPException
from core.firebase import db, get_current_user
from models.schemas import FavoriteRequest
from firebase_admin import firestore

# Khai báo router có tiền tố /auth để gom nhóm các API bảo mật (giống yêu cầu Lab 2)
router = APIRouter(tags=["User"])

# 1. API lấy thông tin cá nhân (Đã đổi từ /me sang /auth/me theo yêu cầu)
@router.get("/auth/me")
def get_my_info(user=Depends(get_current_user)):
    """Lấy thông tin của người dùng hiện tại từ token."""
    return {
        "uid": user.get("uid"),
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture")
    }

# 2. API Lưu địa điểm yêu thích
@router.post("/favorites")
def add_favorite(fav: FavoriteRequest, user=Depends(get_current_user)):
    """Lưu một địa điểm vào danh sách yêu thích của người dùng trên Firestore."""
    if not db:
        raise HTTPException(status_code=500, detail="Database chưa được kết nối")
    
    uid = user.get("uid")
    try:
        doc_ref = db.collection('users').document(uid).collection('favorites').document(str(fav.destination_id))
        doc_ref.set({
            "destination_id": fav.destination_id,
            "destination_name": fav.destination_name,
            "added_at": firestore.SERVER_TIMESTAMP
        })
        return {"message": f"Đã thêm {fav.destination_name} vào danh sách yêu thích"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu vào Firestore: {e}")

# 3. API Đọc danh sách yêu thích
@router.get("/favorites")
def get_favorites(user=Depends(get_current_user)):
    """Lấy danh sách các địa điểm yêu thích của người dùng."""
    if not db:
        raise HTTPException(status_code=500, detail="Database chưa được kết nối")
        
    uid = user.get("uid")
    try:
        danh_sach_yeu_thich = []
        docs = db.collection('users').document(uid).collection('favorites').stream()
        for doc in docs:
            danh_sach_yeu_thich.append(doc.to_dict())
        return {"favorites": danh_sach_yeu_thich}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi đọc từ Firestore: {e}")

# 4. API Đọc Lịch sử tìm kiếm (Mới bổ sung theo yêu cầu Lab 2)
@router.get("/history")
def get_search_history(user=Depends(get_current_user)):
    """Lấy danh sách lịch sử tìm kiếm của người dùng."""
    if not db:
        raise HTTPException(status_code=500, detail="Database chưa được kết nối")
        
    uid = user.get("uid")
    try:
        history = []
        # .order_by giúp sắp xếp lịch sử từ mới nhất đến cũ nhất
        docs = db.collection('users').document(uid).collection('search_history').order_by("timestamp", direction=firestore.Query.DESCENDING).limit(50).stream()
        for doc in docs:
            history.append(doc.to_dict())
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi đọc lịch sử từ Firestore: {e}")
