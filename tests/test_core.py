from datetime import date

import pytest
from fastapi import HTTPException

from app.main import dates
from app.pipeline import generate
from app.statistics import checkout_experiment, sample_size


def test_seed_is_deterministic():
    assert generate(1) == generate(1)


def test_orders_and_refunds_are_consistent():
    data = generate(1)
    signups = {row[0]:row[1] for row in data["customers"]}
    sales = dict.fromkeys((order[0] for order in data["orders"]),0)
    order_dates = {order[0]:order[2] for order in data["orders"]}
    for order_id, customer_id, ordered, _, _ in data["orders"]:
        assert signups[customer_id] <= ordered
    for order_id, product_id, quantity, price, cost, discount in data["items"]:
        assert 1 <= product_id <= len(data["products"])
        assert 0 <= discount <= price
        assert 0 <= cost <= price
        sales[order_id] += quantity*(price-discount)
    assert all(sales.values())
    for order_id, amount, refunded in data["refunds"]:
        assert 0 < amount <= sales[order_id]
        assert order_dates[order_id] < refunded


def test_known_proportion_example():
    result = checkout_experiment({"Control":(100,20), "Treatment":(100,30)})
    assert result["p_value"] == pytest.approx(0.10247, abs=.00001)
    assert result["effect_pp"] == pytest.approx(10)
    assert result["ci_low_pp"] < 0 < result["ci_high_pp"]


def test_empty_and_sparse_experiment():
    assert checkout_experiment({})["control_sessions"] == 0
    assert checkout_experiment({"Control":(10,0),"Treatment":(10,0)})["p_value"] is None


def test_sample_size():
    assert sample_size(.10,.12) == 3841
    with pytest.raises(ValueError):
        sample_size(.1,.1)


def test_reversed_dates():
    with pytest.raises(HTTPException):
        dates(date(2025,1,1),date(2024,1,1))
