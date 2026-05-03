import firebase_admin
from firebase_admin import auth, firestore, credentials
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import time

try:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': 'smarttourism-api'
    })
    db = firestore.client()
    print("Khởi tạo Firebase Admin SDK thành công!")
except Exception as e:
    print(f"Lỗi khởi tạo Firebase: {e}")
    db = None

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        error_msg = str(e)
        if "used too early" in error_msg:
            time.sleep(3)
            try:
                decoded_token = auth.verify_id_token(token)
                return decoded_token
            except Exception as e2:
                error_msg = str(e2)
        raise HTTPException(
            status_code=401,
            detail=f"Token xác thực không hợp lệ: {error_msg}",
            headers={"WWW-Authenticate": "Bearer"},
        )
