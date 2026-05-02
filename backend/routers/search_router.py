from fastapi import APIRouter, HTTPException, Request
from models.schemas import SearchRequest, DestinationResponse
from core.ai_model import model, destination_embeddings
from data.data import tourist_destinations
from sentence_transformers import util
import torch
from core.firebase import db, auth
from firebase_admin import firestore

router = APIRouter(tags=["AI Search"])

# response_model=list[DestinationResponse] quy định rõ kết quả trả về là một Mảng (List) các DestinationResponse.
@router.post("/predict", response_model=list[DestinationResponse])
def predict(request: SearchRequest, req: Request):
    """
    Nhận câu truy vấn từ người dùng, gọi AI để dự đoán.
    Nếu Request có gửi kèm Token đăng nhập, hệ thống sẽ tự động lưu lịch sử tìm kiếm.
    """
    try:
        # Bước 1: Gọi AI để mã hóa câu văn người dùng gửi lên thành Vector
        query_embedding = model.encode(request.query, convert_to_tensor=True)
        
        # Bước 2: Dùng hàm tính góc (Cosine Similarity) để so sánh vector câu hỏi với toàn bộ vector địa điểm
        cosine_scores = util.cos_sim(query_embedding, destination_embeddings)[0]
        
        # Bước 3: Lọc ra top_k điểm cao nhất
        # min(request.top_k, len(...)) lấy số nhỏ nhất, tránh bị lỗi nếu đòi 20 kết quả nhưng mình chỉ có 10.
        k = min(request.top_k, len(tourist_destinations))
        top_results = torch.topk(cosine_scores, k=k)
        
        results = []
        # zip() là hàm của Python giúp lồng 2 danh sách lại với nhau để duyệt chung trong 1 vòng lặp.
        for score, idx in zip(top_results[0], top_results[1]):
            relevance_score = score.item() # .item() giúp tách con số float ra khỏi đối tượng Tensor
            
            # Bỏ qua những kết quả có độ tương đồng quá bé (dưới 0.1 nghĩa là chả liên quan gì)
            if relevance_score < 0.1: 
                continue
                
            matched_dest = tourist_destinations[idx.item()]
            results.append(DestinationResponse(
                id=matched_dest["id"],
                name=matched_dest["name"],
                description=matched_dest["description"],
                score=round(relevance_score, 4) # round(số, 4) giúp làm tròn tới 4 chữ số thập phân
            ))

        # --- ĐOẠN NÀY LƯU LỊCH SỬ NẾU USER CÓ ĐĂNG NHẬP ---
        auth_header = req.headers.get('Authorization')
        if auth_header and auth_header.startswith("Bearer ") and db:
            token = auth_header.split(" ")[1] # Cắt bỏ chữ "Bearer " để lấy phần mã Token
            try:
                user = auth.verify_id_token(token)
                uid = user.get("uid")
                db.collection('users').document(uid).collection('search_history').add({
                    "query": request.query,
                    "timestamp": firestore.SERVER_TIMESTAMP,
                    "results_count": len(results)
                })
            except Exception as e:
                pass # Lỗi token (giả mạo, hết hạn...) thì bỏ qua, vẫn cứ trả kết quả tìm kiếm cho họ.

        if not results:
            raise HTTPException(status_code=404, detail="Không tìm thấy địa điểm nào phù hợp.")
            
        return results

    except Exception as e:
        # isinstance(e, HTTPException) kiểm tra xem lỗi này có phải do chính ta chủ động ném ra ở trên không.
        if isinstance(e, HTTPException): 
            raise e
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")
