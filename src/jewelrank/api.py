from contextlib import asynccontextmanager
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from jewelrank.catalog import seed_catalog
from jewelrank.config import get_settings
from jewelrank.database import SessionLocal, get_session, init_database
from jewelrank.models import CatalogItem, RecommendationEvent
from jewelrank.ranking import rank_catalog
from jewelrank.schemas import (
    Recommendation,
    RecommendationRequest,
    RecommendationResponse,
    ScoreBreakdown,
)

SessionDependency = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    with SessionLocal() as session:
        seed_catalog(session)
    yield


app = FastAPI(
    title="JewelRank API",
    version="1.0.0",
    description="Explainable recommendations over a deterministic synthetic catalog.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/catalog")
def catalog(session: SessionDependency, limit: int = 20) -> list[dict]:
    items = session.scalars(select(CatalogItem).order_by(CatalogItem.id).limit(min(limit, 100)))
    return [
        {
            "sku": item.sku,
            "name": item.name,
            "category": item.category,
            "material": item.material,
            "price": item.price,
            "styles": item.styles,
            "colors": item.colors,
            "segment": item.segment,
        }
        for item in items
    ]


@app.post("/recommend", response_model=RecommendationResponse)
def recommend(request: RecommendationRequest, session: SessionDependency) -> RecommendationResponse:
    items = list(session.scalars(select(CatalogItem)))
    ranked = rank_catalog(items, request)
    request_id = str(uuid4())
    recommendations = [
        Recommendation(
            sku=result.item.sku,
            name=result.item.name,
            category=result.item.category,
            material=result.item.material,
            price=result.item.price,
            styles=result.item.styles,
            colors=result.item.colors,
            segment=result.item.segment,
            score=round(result.score, 4),
            explanation=ScoreBreakdown(
                style=round(result.style_score, 4),
                color=round(result.color_score, 4),
                segment=round(result.segment_score, 4),
            ),
        )
        for result in ranked
    ]
    event = RecommendationEvent(
        request_id=request_id,
        request_payload=request.model_dump(),
        result_count=len(recommendations),
        top_score=recommendations[0].score if recommendations else 0.0,
    )
    session.add(event)
    session.commit()
    return RecommendationResponse(request_id=request_id, recommendations=recommendations)


@app.get("/analytics")
def analytics(session: SessionDependency) -> dict[str, int | float]:
    catalog_size = session.scalar(select(func.count()).select_from(CatalogItem)) or 0
    requests = session.scalar(select(func.count()).select_from(RecommendationEvent)) or 0
    average_top_score = session.scalar(select(func.avg(RecommendationEvent.top_score))) or 0.0
    return {
        "catalog_size": catalog_size,
        "recommendation_requests": requests,
        "average_top_score": round(float(average_top_score), 4),
    }
