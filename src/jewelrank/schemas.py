from pydantic import BaseModel, Field, model_validator


class RecommendationRequest(BaseModel):
    styles: list[str] = Field(default_factory=list, max_length=8)
    colors: list[str] = Field(default_factory=list, max_length=8)
    category: str | None = None
    min_price: int = Field(default=0, ge=0)
    max_price: int = Field(default=10_000, ge=0)
    limit: int = Field(default=6, ge=1, le=20)

    @model_validator(mode="after")
    def validate_price_range(self):
        if self.min_price > self.max_price:
            raise ValueError("min_price must not exceed max_price")
        return self


class ScoreBreakdown(BaseModel):
    style: float
    color: float
    segment: float


class Recommendation(BaseModel):
    sku: str
    name: str
    category: str
    material: str
    price: int
    styles: list[str]
    colors: list[str]
    segment: str
    score: float
    explanation: ScoreBreakdown


class RecommendationResponse(BaseModel):
    request_id: str
    recommendations: list[Recommendation]
