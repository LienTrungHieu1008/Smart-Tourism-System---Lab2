# LAB 2: API & FIREBASE STUDIO

**Môn học:** Tư duy tính toán

**GVHD:** Lê Đức Khoan

**Sinh viên thực hiện:** Liên Trung Hiếu - 24120049

---

## 1. MÔ TẢ DỰ ÁN

Ứng dụng **Smart Tourism** là một hệ thống gợi ý du lịch thông minh, sử dụng **Semantic Search** để trả về các địa điểm phù hợp nhất dựa trên câu truy vấn bằng ngôn ngữ tự nhiên của người dùng. Hệ thống được xây dựng trên nền tảng **FastAPI** (Backend) và giao diện **HTML/CSS/JavaScript thuần** (Frontend).

### Tính năng chính
- **Tìm kiếm thông minh**: Sử dụng Embedding Model để hiểu ý nghĩa câu hỏi và tìm địa điểm tương ứng.
- **Xác thực người dùng**: Tích hợp **Firebase Authentication** để quản lý tài khoản.
- **Quản lý dữ liệu**: Lưu trữ lịch sử tìm kiếm và địa điểm yêu thích của người dùng trên **Firebase Firestore**.
- **API Endpoint**:
    - `/predict`: Nhận câu hỏi và trả về kết quả gợi ý.
    - `/auth/me`: Lấy thông tin người dùng hiện tại.
    - `/favorites`, `/history`: Quản lý dữ liệu cá nhân.

## 2. HƯỚNG DẪN CÀI ĐẶT ENVIRONMENT

**Yêu cầu hệ thống:**
- Python 3.10 trở lên
- Google Cloud CLI (gcloud)

**Các bước cài đặt:**

1. Clone repository về máy:
```bash
git clone https://github.com/LienTrungHieu1008/Smart-Tourism-API-Lab2.git
cd Smart-Tourism-API-Lab2
```

2. Cài đặt các thư viện phụ thuộc:
```bash
pip install -r requirements.txt
```

3. Xác thực Firebase (Application Default Credentials):
Chạy lệnh sau và đăng nhập bằng tài khoản Google đã liên kết với dự án Firebase. Đảm bảo cấp quyền truy cập đầy đủ khi trình duyệt yêu cầu:
```bash
gcloud auth application-default login
```

## 3. HƯỚNG DẪN CHẠY BACKEND

Backend được xây dựng bằng FastAPI. Để khởi động máy chủ:

1. Di chuyển vào thư mục backend:
```bash
cd backend
```

2. Chạy ứng dụng thông qua Uvicorn:
```bash
uvicorn main:app --reload
```

Máy chủ sẽ khởi chạy tại địa chỉ: `http://127.0.0.1:8000`
Tài liệu API (Swagger UI) có sẵn tại: `http://127.0.0.1:8000/docs`

## 4. HƯỚNG DẪN CHẠY FRONTEND

Frontend được xây dựng bằng HTML, CSS và JavaScript thuần (Vanilla JS).

1. Mở thư mục dự án bằng Visual Studio Code.
2. Đảm bảo đã cài đặt extension "Live Server".
3. Nhấp chuột phải vào file `frontend/index.html` và chọn "Open with Live Server".
4. Trình duyệt sẽ tự động mở ứng dụng tại địa chỉ: `http://127.0.0.1:5500`

## 5. ĐƯỜNG DẪN ĐẾN VIDEO DEMO

Video demo giới thiệu ứng dụng, hướng dẫn chạy hệ thống, thử nghiệm các tính năng tìm kiếm và xem dữ liệu được lưu trong Firebase.

**Link Video:** [Chèn link YouTube/Google Drive của bạn vào đây]

---

## 6. THÔNG TIN BỔ SUNG

### Cấu trúc thư mục chính
- `frontend/`: Chứa giao diện người dùng (index.html, style.css, app.js).
- `backend/`: Chứa mã nguồn máy chủ (FastAPI).
  - `core/`: Cấu hình hệ thống (Firebase, AI Model).
  - `models/`: Định nghĩa cấu trúc dữ liệu (Pydantic).
  - `routers/`: Các endpoint API.
  - `data/`: Dữ liệu mẫu.

### Danh sách API Endpoints
- `GET /`: Kiểm tra thông tin hệ thống.
- `GET /health`: Kiểm tra trạng thái hoạt động.
- `POST /predict`: Gợi ý điểm đến bằng AI (Feature chính).
- `GET /auth/me`: Lấy thông tin người dùng hiện tại (Yêu cầu Token).
- `POST /favorites`: Lưu địa điểm yêu thích (Yêu cầu Token).
- `GET /favorites`: Lấy danh sách yêu thích (Yêu cầu Token).
- `GET /history`: Lấy lịch sử tìm kiếm (Yêu cầu Token).
