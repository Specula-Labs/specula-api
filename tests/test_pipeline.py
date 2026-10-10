"""Unit tests for the deterministic baseline scorer in app.agents.pipeline."""

from app.agents.pipeline import RISK_THRESHOLD, run_pipeline

ADDRESS = "G" + "A" * 55


def test_zero_activity_scores_zero_and_low():
    result = run_pipeline(ADDRESS, 0, 0)
    assert result["score"] == 0
    assert result["risk_level"] == "low"
    assert result["threshold"] == RISK_THRESHOLD
    assert result["threshold_exceeded"] is False
    assert result["score_breakdown"]["transaction_activity"] == 0.0
    assert result["score_breakdown"]["transaction_volume"] == 0.0


def test_transaction_count_cap_contributes_sixty_points():
    result = run_pipeline(ADDRESS, 100, 0)
    assert result["score_breakdown"]["transaction_activity"] == 60.0


def test_transaction_volume_cap_contributes_forty_points():
    result = run_pipeline(ADDRESS, 0, 1_000_000)
    assert result["score_breakdown"]["transaction_volume"] == 40.0


def test_components_saturate_at_their_caps():
    result = run_pipeline(ADDRESS, 10_000, 10_000_000)
    assert result["score_breakdown"]["transaction_activity"] == 60.0
    assert result["score_breakdown"]["transaction_volume"] == 40.0
    assert result["score"] == 100
    assert result["score"] <= 100


def test_score_at_risk_threshold_is_high_and_exceeded():
    # 100 transactions (60 pts) + 250,000 XLM volume (10 pts) == RISK_THRESHOLD.
    result = run_pipeline(ADDRESS, 100, 250_000)
    assert result["score"] == RISK_THRESHOLD
    assert result["threshold"] == RISK_THRESHOLD
    assert result["threshold_exceeded"] is True
    assert result["risk_level"] == "high"


def test_elevated_band_covers_scores_below_the_threshold():
    score_40 = run_pipeline(ADDRESS, 0, 1_000_000)
    assert score_40["score"] == 40
    assert score_40["risk_level"] == "elevated"

    result = run_pipeline(ADDRESS, 34, 1_000_000)
    assert 40 <= result["score"] < RISK_THRESHOLD
    assert result["threshold_exceeded"] is False
    assert result["risk_level"] == "elevated"
import pytest
from app.agents.pipeline import run_pipeline, RISK_THRESHOLD, TX_COUNT_CAP, VOLUME_XLM_CAP
@pytest.mark.parametrize(
    "count,volume,score,activity,volume_score,level,exceeded",
    [
        (0, 0, 0, 0.0, 0.0, "low", False),
        (100, 0, 60, 60.0, 0.0, "elevated", False),
        (0, 1_000_000, 40, 0.0, 40.0, "elevated", False),
        (101, 1_000_001, 100, 60.0, 40.0, "high", True),
        (1000, 10_000_000, 100, 60.0, 40.0, "high", True),
        (50, 250_000, 40, 30.0, 10.0, "elevated", False),
        (50, 225_000, 39, 30.0, 9.0, "low", False),
        (50, 275_000, 41, 30.0, 11.0, "elevated", False),
        (100, 225_000, 69, 60.0, 9.0, "elevated", False),
        (100, 250_000, 70, 60.0, 10.0, "high", True),
        (100, 275_000, 71, 60.0, 11.0, "high", True),
    ],
)
def test_pipeline_contract(count, volume, score, activity, volume_score, level, exceeded):
    result = run_pipeline("synthetic-account", count, volume)
    assert result["address"] == "synthetic-account"
    assert result["score"] == score
    assert result["score_breakdown"] == {
        "transaction_activity": activity,
        "transaction_volume": volume_score,
    }
    assert result["risk_level"] == level
    assert result["threshold_exceeded"] is exceeded
    assert result["threshold"] == 70
    assert result["on_chain_action"] == "none"
def test_documented_threshold_is_stable():
    assert RISK_THRESHOLD == 70
    assert TX_COUNT_CAP == 100
    assert VOLUME_XLM_CAP == 1_000_000
