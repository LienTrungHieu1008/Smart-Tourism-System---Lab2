import firebase_admin
from firebase_admin import auth, firestore, credentials
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# ---------------------------------------------------------
# BÀI HỌC PYTHON DÀNH CHO BẠN:
# Khối lệnh try-except dùng để "Bắt lỗi" (Error Handling).
# Nếu các lệnh bên trong chữ 'try' chạy bị lỗi (ví dụ không kết nối được mạng), 
# chương trình sẽ không bị đứng (crash) ngay lập tức, mà sẽ nhảy xuống phần 'except'
# để thực hiện kế hoạch dự phòng.
# ---------------------------------------------------------

try:
    # credentials.ApplicationDefault() tự động tìm file chìa khóa mà lệnh gcloud đã tạo ra trên máy bạn
    cred = credentials.ApplicationDefault()
    
    # options chứa mã định danh dự án Firebase của bạn (lấy từ Firebase Console)
    firebase_admin.initialize_app(cred, {
        'projectId': 'smart-tourism-e91aa'
    })
    
    # db là biến lưu trữ kết nối cơ sở dữ liệu. 
    # Ta khai báo ở đây để các file khác có thể 'import db' ra và dùng chung.
    db = firestore.client()
    print("Khởi tạo Firebase Admin SDK thành công!")
except Exception as e:
    print(f"Lỗi khởi tạo Firebase: {e}")
    db = None # Nếu lỗi, ta gán db là rỗng để app không chết, nhưng sẽ không lưu dữ liệu được

# HTTPBearer là công cụ của FastAPI giúp tạo ra ô nhập "Token" trên giao diện Swagger UI
security = HTTPBearer()

# Hàm get_current_user này đóng vai trò là Dependency (Phụ thuộc). 
# Nó giống như một "Bảo vệ gác cổng". Các API quan trọng sẽ gắn hàm này vào tham số để soát vé.
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # credentials.credentials chính là chuỗi mã hóa dài ngoằng (Token) người dùng gửi lên
    token = credentials.credentials
    try:
        # Nhờ thư viện Firebase giải mã vé này xem vé thật hay giả, có hết hạn chưa.
        decoded_token = auth.verify_id_token(token)
        
        # Nếu vé hợp lệ, nó sẽ trả về thông tin user như uid, email, tên... (dạng Dictionary của Python)
        return decoded_token 
    except Exception as e:
        # Từ khóa 'raise' dùng để chủ động ném ra một lỗi và ngưng chạy API ngay lập tức.
        # 401 là mã lỗi chuẩn quốc tế dành cho "Không có quyền truy cập" (Unauthorized).
        raise HTTPException(
            status_code=401,
            detail=f"Token xác thực không hợp lệ: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
