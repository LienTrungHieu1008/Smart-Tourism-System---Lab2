from fastapi import APIRouter, HTTPException, Request
from models.schemas import SearchRequest, DestinationResponse
from core.ai_model import model, destination_embeddings
from data.data import tourist_destinations
from sentence_transformers import util
import torch
from core.firebase import db, auth
from firebase_admin import firestore

router = APIRouter(tags=["AI Search"])


@router.post("/predict", response_model=list[DestinationResponse])
def predict(request: SearchRequest, req: Request):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Câu truy vấn không được để trống.")
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

        auth_header = req.headers.get('Authorization')
        if auth_header and auth_header.startswith("Bearer ") and db:
            token = auth_header.split(" ")[1]
            try:
                user = auth.verify_id_token(token)
                uid = user.get("uid")
                db.collection('users').document(uid).collection('search_history').add({
                    "query": request.query,
                    "timestamp": firestore.SERVER_TIMESTAMP,
                    "results_count": len(results)
                })
            except Exception:
                pass

        if not results:
            raise HTTPException(status_code=404, detail="Không tìm thấy địa điểm nào phù hợp.")

        return results

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")
