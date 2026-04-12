from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer, util
import torch
import time
import os

app = FastAPI(title="Smart Tourism API", description="API Suggestion using Semantic Search")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 1. Định nghĩa Models (Pydantic Schema)
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Câu truy vấn tìm kiếm")
    top_k: int = Field(3, gt=0, le=10, description="Số lượng kết quả trả về tối đa")

class DestinationResponse(BaseModel):
    id: int
    name: str
    description: str
    score: float

# 2. Import Mock Data từ file data.py (1000 địa điểm du lịch)
from data import tourist_destinations
from generate_data import generate

# 3. Khởi tạo AI Model và Tính toán Vector
print("Đang tải mô hình Sentence Transformer...")
model = SentenceTransformer('all-MiniLM-L6-v2')

descriptions = [dest["description"] for dest in tourist_destinations]

print("Đang mã hóa dữ liệu văn bản thành vectors embedding...")
destination_embeddings = model.encode(descriptions, convert_to_tensor=True)

#4. API Endpoints
@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.post("/suggest", response_model=list[DestinationResponse])
def suggest_destinations(request: SearchRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Câu truy vấn không hợp lệ (trống hoặc chỉ chứa khoảng trắng).")
    
    try:
        query_embedding = model.encode(request.query, convert_to_tensor=True)
        
        cosine_scores = util.cos_sim(query_embedding, destination_embeddings)[0]
        
        k = min(request.top_k, len(tourist_destinations))
        top_results = torch.topk(cosine_scores, k=k)
        
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            relevance_score = score.item()
            
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
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống trong quá trình tính toán: {str(e)}")

@app.get("/health")
def health_check():
    """Endpoint kiểm tra sức khỏe server.
    Trả về trạng thái hoạt động, thông tin model và số lượng dữ liệu hiện tại."""
    return {
        "status": "healthy",
        "model_name": "all-MiniLM-L6-v2",
        "total_destinations": len(tourist_destinations),
        "embedding_dimensions": destination_embeddings.shape[1] if destination_embeddings is not None else 0,
        "message": "Server đang hoạt động bình thường."
    }


@app.post("/generate")
def generate_data_endpoint():
    """Endpoint sinh lại dữ liệu địa điểm du lịch.
    Chạy lại script generate_data.py để tạo 1000 địa điểm và cập nhật embeddings."""
    global tourist_destinations, descriptions, destination_embeddings

    try:
        start_time = time.time()

        new_data = generate()

        lines = ["# Auto-generated: 1000 Địa điểm du lịch Việt Nam", "tourist_destinations = ["]
        for d in new_data:
            lines.append(f'    {{"id": {d["id"]}, "name": "{d["name"]}", "description": "{d["description"]}"}},')
        lines.append("]")
        lines.append("")

        out_path = os.path.join(os.path.dirname(__file__), "data.py")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        tourist_destinations = new_data
        descriptions = [dest["description"] for dest in tourist_destinations]

        destination_embeddings = model.encode(descriptions, convert_to_tensor=True)

        elapsed = round(time.time() - start_time, 2)

        return {
            "status": "success",
            "total_generated": len(new_data),
            "time_seconds": elapsed,
            "message": f"Đã tạo thành công {len(new_data)} địa điểm và cập nhật embeddings trong {elapsed}s."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi sinh dữ liệu: {str(e)}")