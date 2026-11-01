import json
from pathlib import Path


def test_scheme_catalog_contains_at_least_50_entries():
    root = Path(__file__).resolve().parents[2]
    schemes = json.loads((root / "data/seed/verified_schemes.json").read_text(encoding="utf-8"))
    assert len(schemes) >= 50
    assert len({s["scheme_id"] for s in schemes}) == len(schemes)
    assert all(s.get("official_portal_url") for s in schemes)
