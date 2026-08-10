from pydantic import BaseModel


class ProductResponse(BaseModel):
    name: str
    category: str
    trend_score: int
    stage: str

    tiktok_growth: int
    whatnot_growth: int
    google_growth: int
    competition: int
