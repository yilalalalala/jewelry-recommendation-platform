from sqlalchemy import func, select
from sqlalchemy.orm import Session

from jewelrank.models import CatalogItem

SEGMENTS: dict[str, dict[str, list[str]]] = {
    "classic": {"styles": ["classic", "minimalist"], "colors": ["white", "silver"]},
    "modern": {"styles": ["modern", "minimalist"], "colors": ["black", "silver"]},
    "romantic": {"styles": ["romantic", "classic"], "colors": ["pink", "red"]},
    "bold": {"styles": ["bold", "luxurious"], "colors": ["red", "gold"]},
    "bohemian": {"styles": ["bohemian", "vintage"], "colors": ["green", "blue"]},
    "minimalist": {"styles": ["minimalist", "modern"], "colors": ["white", "gold"]},
    "vintage": {"styles": ["vintage", "romantic"], "colors": ["purple", "gold"]},
    "luxurious": {"styles": ["luxurious", "classic"], "colors": ["white", "gold"]},
}

CATEGORIES = ("ring", "necklace", "bracelet", "earrings")
MATERIALS = ("gold", "silver", "platinum", "ceramic")


def build_synthetic_catalog(items_per_segment: int = 8) -> list[CatalogItem]:
    """Create a deterministic, brand-neutral demo catalog with no scraped product assets."""
    items: list[CatalogItem] = []
    item_id = 1
    for segment, profile in SEGMENTS.items():
        for offset in range(items_per_segment):
            category = CATEGORIES[(item_id - 1) % len(CATEGORIES)]
            material = MATERIALS[(item_id - 1) % len(MATERIALS)]
            price = 120 + 85 * offset + 40 * list(SEGMENTS).index(segment)
            items.append(
                CatalogItem(
                    id=item_id,
                    sku=f"JR-{item_id:04d}",
                    name=f"{segment.title()} {material.title()} {category.title()}",
                    category=category,
                    material=material,
                    price=price,
                    styles=profile["styles"],
                    colors=profile["colors"],
                    segment=segment,
                )
            )
            item_id += 1
    return items


def seed_catalog(session: Session) -> int:
    existing = session.scalar(select(func.count()).select_from(CatalogItem)) or 0
    if existing:
        return 0
    items = build_synthetic_catalog()
    session.add_all(items)
    session.commit()
    return len(items)
