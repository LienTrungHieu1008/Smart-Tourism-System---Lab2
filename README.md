# 🌍 Smart Tourism API

**Ứng dụng gợi ý điểm đến du lịch Việt Nam bằng AI (Semantic Search)**

> Bài thực hành số 2 - Môn Tư Duy Tính Toán  
> Trường Đại học Khoa Học Tự Nhiên - ĐHQG TP.HCM  
> GVHD: Lê Đức Khoan

## 📋 Mô tả

Smart Tourism là ứng dụng web cho phép người dùng tìm kiếm điểm đến du lịch bằng ngôn ngữ tự nhiên. Hệ thống sử dụng mô hình AI **Sentence Transformer (all-MiniLM-L6-v2)** từ Hugging Face để phân tích ngữ nghĩa câu truy vấn và so sánh với cơ sở dữ liệu gồm **1000 địa điểm du lịch** trên khắp Việt Nam.

### Tính năng chính
- 🔍 **Tìm kiếm thông minh**: Nhập câu hỏi tự nhiên (VD: "Tôi muốn đi biển lặn san hô"), AI sẽ gợi ý các điểm đến phù hợp nhất.
- 🔐 **Đăng nhập Google**: Tích hợp Firebase Authentication để xác thực người dùng.
- 💾 **Lưu trữ dữ liệu**: Tự động lưu lịch sử tìm kiếm và danh sách yêu thích lên Firebase Firestore.
- 📱 **Giao diện hiện đại**: Dark Mode, Glassmorphism, Responsive trên mọi thiết bị.

## 🏗️ Cấu trúc thư mục

```
Smart-Tourism-API/
├── frontend/                # Giao diện người dùng
│   ├── index.html           # Trang chính
│   ├── style.css            # Thiết kế giao diện (Dark Mode)
│   └── app.js               # Xử lý đăng nhập Firebase & gọi API
├── backend/                 # Máy chủ xử lý logic
│   ├── main.py              # File chạy chính (Entry Point)
│   ├── core/                # Module cấu hình hệ thống
│   │   ├── firebase.py      # Kết nối Firebase & hàm xác thực Token
│   │   └── ai_model.py      # Khởi tạo mô hình AI & tính Vector
│   ├── models/              # Định nghĩa cấu trúc dữ liệu
│   │   └── schemas.py       # Các class Pydantic (Request/Response)
│   ├── routers/             # Các API endpoint
│   │   ├── search_router.py # API tìm kiếm AI (POST /predict)
│   │   └── user_router.py   # API người dùng (/auth/me, /favorites, /history)
│   └── data/                # Dữ liệu
│       ├── data.py          # 1000 địa điểm du lịch Việt Nam
│       └── generate_data.py # Script sinh dữ liệu
├── README.md
├── requirements.txt
└── .gitignore
```

## ⚙️ Hướng dẫn cài đặt Environment

### Yêu cầu hệ thống
- Python 3.10 trở lên
- Google Cloud CLI (`gcloud`) đã cài đặt
- Tài khoản Firebase (đã tạo dự án và bật Authentication + Firestore)

### Bước 1: Clone repository
```bash
git clone https://github.com/LienTrungHieu1008/Smart-Tourism-API.git
cd Smart-Tourism-API
```

### Bước 2: Cài đặt thư viện Python
```bash
pip install -r requirements.txt
```

### Bước 3: Xác thực Firebase (Application Default Credentials)
```bash
gcloud auth application-default login
```
Trình duyệt sẽ bật lên, đăng nhập bằng tài khoản Google liên kết với dự án Firebase và **tích chọn tất cả các quyền** rồi bấm Allow.

## 🚀 Hướng dẫn chạy Backend

```bash
cd backend
uvicorn main:app --reload
```

Server sẽ khởi chạy tại: `http://127.0.0.1:8000`

Tài liệu API tự động (Swagger UI): `http://127.0.0.1:8000/docs`

## 🎨 Hướng dẫn chạy Frontend

1. Cài Extension **Live Server** trong VSCode.
2. Click chuột phải vào file `frontend/index.html` → chọn **"Open with Live Server"**.
3. Trình duyệt tự động mở tại `http://127.0.0.1:5500`.

## 📡 Danh sách API Endpoints

| Phương thức | Đường dẫn | Mô tả | Yêu cầu Token |
|---|---|---|---|
| `GET` | `/` | Thông tin hệ thống | ❌ |
| `GET` | `/health` | Kiểm tra trạng thái | ❌ |
| `POST` | `/predict` | Gợi ý điểm đến bằng AI | ❌ (Tùy chọn) |
| `GET` | `/auth/me` | Thông tin người dùng hiện tại | ✅ |
| `POST` | `/favorites` | Lưu địa điểm yêu thích | ✅ |
| `GET` | `/favorites` | Xem danh sách yêu thích | ✅ |
| `GET` | `/history` | Xem lịch sử tìm kiếm | ✅ |

## 🛠️ Công nghệ sử dụng

- **Backend**: FastAPI, Uvicorn, Pydantic
- **AI/ML**: Sentence Transformers (Hugging Face), PyTorch
- **Authentication**: Firebase Authentication (Google Login)
- **Database**: Firebase Firestore
- **Frontend**: HTML, CSS (Vanilla), JavaScript (ES Module)

## 🎬 Video Demo

[👉 Xem Video Demo tại đây](https://youtube.com/your-video-link)

## 👤 Thông tin sinh viên

- **Họ tên**: Liên Trung Hiếu
- **MSSV**: 24120049
