from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer, util
import torch

app = FastAPI(
    title="Smart Tourism API",
    description="API gợi ý điểm đến du lịch Việt Nam sử dụng mô hình Sentence Transformer từ Hugging Face để tìm kiếm ngữ nghĩa (Semantic Search).",
    version="1.0.0"
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 1. Định nghĩa Models (Pydantic Schema)
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Câu truy vấn tìm kiếm của người dùng")
    top_k: int = Field(5, gt=0, le=20, description="Số lượng kết quả trả về tối đa")

class DestinationResponse(BaseModel):
    id: int
    name: str
    description: str
    score: float

# 2. Import Mock Data từ file data.py (1000 địa điểm du lịch)
from data import tourist_destinations

# 3. Khởi tạo AI Model và Tính toán Vector
print("Đang tải mô hình Sentence Transformer (all-MiniLM-L6-v2) từ Hugging Face...")
model = SentenceTransformer('all-MiniLM-L6-v2')

descriptions = [dest["description"] for dest in tourist_destinations]

print(f"Đang mã hóa {len(descriptions)} mô tả thành vectors embedding...")
destination_embeddings = model.encode(descriptions, convert_to_tensor=True)
print("Hoàn tất khởi tạo! Server sẵn sàng phục vụ.")

# 4. API Endpoints

@app.get("/")
def read_root():
    """Trả về thông tin giới thiệu hệ thống hoặc trang giao diện web."""
    return {
        "system": "Smart Tourism API",
        "description": "Hệ thống gợi ý điểm đến du lịch Việt Nam sử dụng mô hình Sentence Transformer (all-MiniLM-L6-v2) từ Hugging Face để tìm kiếm ngữ nghĩa.",
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        "huggingface_url": "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2",
        "total_destinations": len(tourist_destinations),
        "endpoints": {
            "GET /": "Thông tin giới thiệu hệ thống",
            "GET /health": "Kiểm tra trạng thái hoạt động",
            "POST /predict": "Gợi ý điểm đến du lịch dựa trên câu truy vấn",
            "GET /ui": "Giao diện web tương tác"
        },
        "usage_example": {
            "endpoint": "POST /predict",
            "request_body": {"query": "tôi muốn đi biển lặn san hô", "top_k": 5},
            "description": "Gửi câu truy vấn để nhận gợi ý điểm đến phù hợp nhất"
        }
    }

@app.get("/ui")
def serve_ui():
    """Trả về giao diện web tương tác."""
    return FileResponse("static/index.html")

@app.get("/health")
def health_check():
    """Kiểm tra trạng thái hoạt động của hệ thống.
    Trả về trạng thái server, thông tin model và số lượng dữ liệu hiện tại."""
    return {
        "status": "healthy",
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "model_source": "Hugging Face",
        "total_destinations": len(tourist_destinations),
        "embedding_dimensions": destination_embeddings.shape[1] if destination_embeddings is not None else 0,
        "message": "Server đang hoạt động bình thường."
    }

@app.post("/predict", response_model=list[DestinationResponse])
def predict(request: SearchRequest):
    """Nhận câu truy vấn từ người dùng, gọi mô hình Hugging Face (Sentence Transformer)
    để tính toán độ tương đồng ngữ nghĩa, và trả về danh sách điểm đến phù hợp nhất dưới dạng JSON.

    - **query**: Câu mô tả nhu cầu du lịch (ví dụ: "tôi muốn leo núi ngắm mây")
    - **top_k**: Số lượng kết quả trả về (mặc định: 5, tối đa: 20)
    """
    # Kiểm tra dữ liệu đầu vào
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Câu truy vấn không hợp lệ (trống hoặc chỉ chứa khoảng trắng).")

    try:
        # Bước 1: Mã hóa câu truy vấn thành vector bằng mô hình Hugging Face
        query_embedding = model.encode(request.query, convert_to_tensor=True)

        # Bước 2: Tính Cosine Similarity giữa query và tất cả điểm đến
        cosine_scores = util.cos_sim(query_embedding, destination_embeddings)[0]

        # Bước 3: Lấy top_k kết quả có điểm cao nhất
        k = min(request.top_k, len(tourist_destinations))
        top_results = torch.topk(cosine_scores, k=k)

        # Bước 4: Chuẩn bị kết quả JSON
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            relevance_score = score.item()

            # Lọc bỏ kết quả có độ tương đồng quá thấp
            if relevance_score < 0.1:
                continue

            matched_dest = tourist_destinations[idx.item()]
            results.append(DestinationResponse(
                id=matched_dest["id"],
                name=matched_dest["name"],
                description=matched_dest["description"],
                score=round(relevance_score, 4)
            ))

        if not results:
            raise HTTPException(status_code=404, detail="Không tìm thấy địa điểm nào phù hợp với yêu cầu của bạn.")

        return results

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống trong quá trình suy luận: {str(e)}")