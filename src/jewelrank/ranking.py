from dataclasses import dataclass

from jewelrank.models import CatalogItem
from jewelrank.schemas import RecommendationRequest

STYLE_WEIGHT = 0.55
COLOR_WEIGHT = 0.30
SEGMENT_WEIGHT = 0.15


@dataclass(frozen=True)
class RankedItem:
    item: CatalogItem
    score: float
    style_score: float
    color_score: float
    segment_score: float


def overlap_score(preferences: set[str], attributes: set[str]) -> float:
    if not preferences:
        return 0.5
    return len(preferences & attributes) / len(preferences)


def rank_catalog(items: list[CatalogItem], request: RecommendationRequest) -> list[RankedItem]:
    requested_styles = {value.lower() for value in request.styles}
    requested_colors = {value.lower() for value in request.colors}
    requested_category = request.category.lower() if request.category else None
    ranked: list[RankedItem] = []

    for item in items:
        if not request.min_price <= item.price <= request.max_price:
            continue
        if requested_category and item.category.lower() != requested_category:
            continue

        style = overlap_score(requested_styles, {value.lower() for value in item.styles})
        color = overlap_score(requested_colors, {value.lower() for value in item.colors})
        segment = 1.0 if item.segment.lower() in requested_styles else 0.0
        score = STYLE_WEIGHT * style + COLOR_WEIGHT * color + SEGMENT_WEIGHT * segment
        ranked.append(RankedItem(item, score, style, color, segment))

    ranked.sort(key=lambda result: (-result.score, result.item.price, result.item.sku))
    return ranked[: request.limit]
