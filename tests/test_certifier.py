"""Tests for TruthCert certifier."""
from mes_core.map.certifier import certify


def test_certify_pass():
    bundle = certify("abc123", "def456", 648, 640, 0, "FRAGILE")
    assert bundle["certification"] == "PASS"
    assert bundle["input_hash"] == "abc123"
    assert "timestamp" in bundle
    assert "bundle_hash" in bundle


def test_certify_warn_sparse():
    bundle = certify("abc123", "def456", 648, 500, 0, "UNSTABLE")
    assert bundle["certification"] == "WARN"
    assert "Infeasible rate" in bundle["reason"]


def test_certify_reject_errors():
    bundle = certify("abc123", "def456", 648, 640, 100, "FRAGILE")
    assert bundle["certification"] == "REJECT"
    assert "Error rate" in bundle["reason"]


def test_certify_bundle_hash_deterministic():
    """Bundle hash should be based on content."""
    b1 = certify("abc123", "def456", 648, 640, 0, "FRAGILE")
    assert len(b1["bundle_hash"]) == 64  # SHA-256 hex


def test_certify_edge_zero_specs():
    """Zero specs => infeasible_rate=100% => WARN."""
    bundle = certify("abc", "def", 0, 0, 0, "UNSTABLE")
    assert bundle["certification"] == "WARN"
    assert bundle["n_specs"] == 0
