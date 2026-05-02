from sentence_transformers import SentenceTransformer, util
import torch

# Import biến tourist_destinations (chứa 1000 địa điểm) từ file data.py ở thư mục ngoài cùng
from data.data import tourist_destinations

# Lần đầu chạy hàm này, máy sẽ hơi giật/chậm vì phải tải mô hình AI nặng vài chục MB từ mạng về.
print("Đang tải mô hình AI Sentence Transformer (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# ---------------------------------------------------------
# BÀI HỌC PYTHON DÀNH CHO BẠN (List Comprehension):
# Đoạn code bên dưới là một "ma thuật" thu gọn code cực hay của Python.
# Thay vì phải viết vòng lặp dài 3 dòng:
#   descriptions = []
#   for dest in tourist_destinations:
#       descriptions.append(dest["description"])
# Python cho phép ta viết gộp lại trên một dòng duy nhất cho gọn và chạy nhanh hơn.
# ---------------------------------------------------------
descriptions = [dest["description"] for dest in tourist_destinations]

print("Đang tính toán Vectors cho toàn bộ địa điểm, vui lòng đợi...")

# Mã hóa tất cả các đoạn văn mô tả thành Vector (chuỗi số toán học).
# convert_to_tensor=True giúp kết quả tạo ra tương thích với thư viện tính toán tốc độ cao PyTorch.
# Biến destination_embeddings này sẽ nằm im trong bộ nhớ RAM để chờ khách hàng tìm kiếm là lôi ra tính điểm.
destination_embeddings = model.encode(descriptions, convert_to_tensor=True)

print("Hoàn tất chuẩn bị AI!")
