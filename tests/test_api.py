def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_recommendation_contract_and_analytics(client):
    response = client.post(
        "/recommend",
        json={"styles": ["modern"], "colors": ["black"], "category": "ring", "limit": 3},
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["request_id"]) == 36
    assert 1 <= len(payload["recommendations"]) <= 3
    recommendation = payload["recommendations"][0]
    assert recommendation["score"] >= 0
    assert set(recommendation["explanation"]) == {"style", "color", "segment"}

    analytics = client.get("/analytics").json()
    assert analytics["catalog_size"] == 64
    assert analytics["recommendation_requests"] == 1


def test_invalid_price_range_returns_422(client):
    response = client.post("/recommend", json={"min_price": 500, "max_price": 100})
    assert response.status_code == 422
