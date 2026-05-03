from sentence_transformers import SentenceTransformer
from data.data import tourist_destinations

print("Đang tải mô hình AI Sentence Transformer (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

descriptions = [dest["description"] for dest in tourist_destinations]

print("Đang tính toán Vectors cho toàn bộ địa điểm, vui lòng đợi...")
destination_embeddings = model.encode(descriptions, convert_to_tensor=True)
print("Hoàn tất chuẩn bị AI!")
