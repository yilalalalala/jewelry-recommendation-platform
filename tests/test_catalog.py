from jewelrank.catalog import SEGMENTS, build_synthetic_catalog, seed_catalog
from jewelrank.models import CatalogItem


def test_catalog_is_deterministic_and_brand_neutral():
    first = build_synthetic_catalog()
    second = build_synthetic_catalog()
    assert len(first) == len(SEGMENTS) * 8
    assert [item.sku for item in first] == [item.sku for item in second]
    assert all("cartier" not in item.name.lower() for item in first)


def test_seed_catalog_is_idempotent(session):
    assert seed_catalog(session) == 64
    assert seed_catalog(session) == 0
    assert session.query(CatalogItem).count() == 64
