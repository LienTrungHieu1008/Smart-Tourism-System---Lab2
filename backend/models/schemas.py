from pydantic import BaseModel, Field

# ---------------------------------------------------------
# BÀI HỌC PYTHON DÀNH CHO BẠN:
# - BaseModel là một "khuôn đúc" được cung cấp bởi thư viện Pydantic.
# - Khi một class kế thừa (inherit) từ BaseModel, Python/FastAPI sẽ tự động 
#   ép kiểu và kiểm tra lỗi dữ liệu đầu vào.
# - Ví dụ: Nếu bạn bắt buộc 'top_k' là số nguyên (int) nhưng người dùng gửi 
#   lên chữ "mười", Pydantic sẽ tự động từ chối và báo lỗi giúp bạn.
# ---------------------------------------------------------

class SearchRequest(BaseModel):
    # Dấu '...' trong hàm Field() có nghĩa là trường dữ liệu này BẮT BUỘC phải có (Required).
    # min_length=1: Cấm người dùng gửi câu tìm kiếm rỗng "".
    query: str = Field(..., min_length=1, description="Câu truy vấn tìm kiếm của người dùng")
    
    # 'top_k' không bắt buộc, nếu người dùng không gửi, mặc định sẽ lấy giá trị là 5.
    # gt=0 (greater than 0), le=20 (less than or equal 20) -> Giới hạn từ 1 đến 20.
    top_k: int = Field(5, gt=0, le=20, description="Số lượng kết quả trả về tối đa")

class DestinationResponse(BaseModel):
    # Đây là khuôn mẫu định nghĩa dạng dữ liệu trả về cho client.
    # Nhờ khai báo các dòng này, FastAPI có thể tự động tạo ra file tài liệu Swagger UI rất đẹp.
    id: int
    name: str
    description: str
    score: float # float là kiểu số thập phân (số thực), ví dụ: 0.85

class FavoriteRequest(BaseModel):
    destination_id: int
    destination_name: str
