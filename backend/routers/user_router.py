from fastapi import APIRouter, Depends, HTTPException
from core.firebase import db, get_current_user
from models.schemas import FavoriteRequest
from firebase_admin import firestore

router = APIRouter(tags=["User"])


@router.get("/auth/me")
def get_my_info(user=Depends(get_current_user)):
    return {
        "uid": user.get("uid"),
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture")
    }


@router.post("/favorites")
def add_favorite(fav: FavoriteRequest, user=Depends(get_current_user)):
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


@router.get("/favorites")
def get_favorites(user=Depends(get_current_user)):
    if not db:
        raise HTTPException(status_code=500, detail="Database chưa được kết nối")
    uid = user.get("uid")
    try:
        result = []
        docs = db.collection('users').document(uid).collection('favorites').stream()
        for doc in docs:
            result.append(doc.to_dict())
        return {"favorites": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi đọc từ Firestore: {e}")


@router.get("/history")
def get_search_history(user=Depends(get_current_user)):
    if not db:
        raise HTTPException(status_code=500, detail="Database chưa được kết nối")
    uid = user.get("uid")
    try:
        history = []
        docs = (
            db.collection('users')
            .document(uid)
            .collection('search_history')
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(50)
            .stream()
        )
        for doc in docs:
            history.append(doc.to_dict())
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi đọc lịch sử từ Firestore: {e}")
