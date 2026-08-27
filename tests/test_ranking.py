from jewelrank.catalog import build_synthetic_catalog
from jewelrank.ranking import COLOR_WEIGHT, SEGMENT_WEIGHT, STYLE_WEIGHT, rank_catalog
from jewelrank.schemas import RecommendationRequest


def test_weights_sum_to_one():
    assert STYLE_WEIGHT + COLOR_WEIGHT + SEGMENT_WEIGHT == 1.0


def test_ranking_prefers_matching_segment_and_is_deterministic():
    request = RecommendationRequest(styles=["romantic"], colors=["pink"], limit=4)
    first = rank_catalog(build_synthetic_catalog(), request)
    second = rank_catalog(build_synthetic_catalog(), request)
    assert [result.item.sku for result in first] == [result.item.sku for result in second]
    assert all(result.item.segment == "romantic" for result in first)
    assert all(first[index].score >= first[index + 1].score for index in range(len(first) - 1))


def test_ranking_respects_budget_and_category():
    request = RecommendationRequest(category="ring", min_price=200, max_price=500, limit=20)
    results = rank_catalog(build_synthetic_catalog(), request)
    assert results
    assert all(result.item.category == "ring" for result in results)
    assert all(200 <= result.item.price <= 500 for result in results)
