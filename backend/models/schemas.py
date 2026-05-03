from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Câu truy vấn tìm kiếm của người dùng")
    top_k: int = Field(5, gt=0, le=20, description="Số lượng kết quả trả về tối đa")


class DestinationResponse(BaseModel):
    id: int
    name: str
    description: str
    score: float


class FavoriteRequest(BaseModel):
    destination_id: int
    destination_name: str
